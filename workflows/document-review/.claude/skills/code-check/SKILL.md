---
name: code-check
description: Cross-reference documentation claims against actual source code.
---

# Code Check Documentation Skill

You are cross-referencing a project's documentation against its actual source
code to verify accuracy. This is a deeper accuracy check than the
`/quality-review` phase, which only evaluates documentation in isolation.

You work in three stages:

1. **Reconnaissance** — Detect languages, frameworks, and components
2. **Discovery** — Dispatch parallel agents to build a code inventory
3. **Verification** — Cross-reference the code inventory against documentation

## Critical Rules

- **Read the inventory first.** This phase requires `/scan` to have been run.
  If `artifacts/inventory.md` does not exist, inform the user and recommend
  running `/scan` first.
- **Read, don't run.** This is static analysis — read source code, don't
  execute it.
- **Be precise.** Every finding must include a direct quote from the
  documentation AND an actual code snippet. Use fenced code blocks with
  language tags.
- **Flag undocumented features.** Code functionality with no documentation is
  a High finding. When checking a code area (e.g., a struct or route group),
  scan all fields/routes — not just what docs mention.
- **Separate uncertain findings.** Low-confidence findings go in a dedicated
  section, not in the main findings. Fuzzy name matches (e.g., `MAAS_DB_HOST`
  vs `DB_HOST`) belong in Low-Confidence.

## Stage 1: Reconnaissance

Perform this yourself — no agents needed. This determines which discovery
agents to spawn in Stage 2.

### Step 1.1: Language & Framework Detection

Use Glob to check for these signature files in the project root and
subdirectories:

| File | Language/Framework |
|------|-------------------|
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `package.json` | Node.js/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python |
| `pom.xml`, `build.gradle` | Java |
| `Gemfile` | Ruby |

For detected languages, check framework markers:

- Go: `go.mod`/`go.sum` for `controller-runtime`, `cobra`, `gin`, `echo`,
  `chi`
- Python: `pyproject.toml`/`requirements.txt` for `fastapi`, `flask`,
  `django`, `click`
- Node.js: `package.json` for `express`, `next`, `nestjs`, `commander`
- Java: `pom.xml`/`build.gradle` for `spring-boot`, `spring-web`, `quarkus`,
  `micronaut`, `picocli`, `javax.ws.rs` (JAX-RS)
- Ruby: `Gemfile` for `rails`, `sinatra`, `grape`, `thor`

### Step 1.2: Component Detection

Use Glob to find multiple `go.mod`, `package.json`, `Cargo.toml`,
`pyproject.toml` files. Each distinct directory containing one (that is NOT
the project root) is a component. Also check for directories with their own
`README.md` + `Makefile` or `Dockerfile`.

### Step 1.3: Category Applicability

Determine which discovery agents to spawn:

| Category | Reference file | Spawn condition |
|----------|---------------|----------------|
| Env vars | `discovery-env-vars.md` | Always |
| CLI args | `discovery-cli-args.md` | Entry points found (`main.go`, `main.py`, `bin/`, CLI framework) |
| Config schema | `discovery-config-schema.md` | Config files or config library imports |
| API schema | `discovery-api-schema.md` | OpenAPI specs, protobuf, HTTP framework imports |
| Data models | `discovery-data-models.md` | CRD directories, migration files, ORM imports |
| File I/O | `discovery-file-io.md` | File write operations or output file references in docs |
| External deps | `discovery-external-deps.md` | Database drivers, HTTP clients, message queues |
| Build/deploy | `discovery-build-deploy.md` | Makefiles, Dockerfiles, CI configs |

### Step 1.4: Compile Project Profile

Build a concise profile block to pass to discovery agents:

```text
PROJECT PROFILE
Languages: Go, Python
Frameworks: controller-runtime, cobra
Components:
  - maas-api (Go) — maas-api/
  - maas-controller (Go) — maas-controller/
Discovery agents to spawn: env-vars, cli-args, api-schema, data-models, build-deploy
```

## Stage 2: Discovery

Dispatch discovery agents in PARALLEL using the Agent tool with
`subagent_type: Explore`.

For each agent to spawn:

1. Read the agent's prompt template from
   `.claude/skills/code-check/references/discovery-{category}.md`
2. Read the inventory format spec from
   `.claude/skills/code-check/references/inventory-format.md`
3. Construct the agent prompt by concatenating:
   - The project profile from Stage 1
   - The agent's prompt template
   - The inventory format spec
4. Dispatch via Agent tool with `subagent_type: Explore`

Issue ALL Agent tool calls in a SINGLE response to maximize parallelism.

**Per-component splitting:** For projects with 4+ components, consider
spawning per-component agents for categories like API Schema or Data Models
(e.g., one API Schema agent for `maas-api/`, another for
`maas-controller/`). Include the component path scope in the agent prompt.

### Merge Discovery Results

After all agents return:

1. Collect all inventory fragments
2. Empty fragments (zero items) are valid — record as "no items found"
3. For failed agents: log the failure, continue with others
4. Deduplicate:
   - Primary match: item name (exact) + type
   - Secondary match: same source file and line across agents
   - Merge source locations into single entry
   - For conflicting values: preserve conflict explicitly (e.g.,
     `Default: "30" (per config-schema agent) / "90" (per env-vars agent)`)
   - Use entry with most non-null fields as base
   - Use the env var name as the canonical item name when the item is an
     environment variable
5. Organize by workflow (installation, then usage, then both), then by
   category within each section

Hold the merged code inventory in context for Stage 3.

## Stage 3: Verification

Cross-reference the code inventory against the documentation files cataloged
in `artifacts/inventory.md`.

### What to Check

For each documentation file, identify claims about code behavior and compare
against the code inventory:

**Accuracy — do docs match code?**

- API endpoints: routes, methods, paths, auth requirements
- CLI flags: names, types, defaults, help text
- Config options: field names, types, defaults
- Default values: what the code actually sets
- Behavior descriptions: auth flows, error handling, rate limiting

**Completeness — are code features documented?**

- Code inventory items with NO mention in any documentation file
- CRD fields, API endpoints, CLI flags, env vars missing from docs
- Runtime behaviors not explained

**Staleness — do docs reference things that no longer exist?**

- Env vars, CLI flags, API endpoints, config fields in docs but NOT in the
  code inventory — confirm absence with Grep/Glob before reporting
- File paths that don't exist in the repo
- Components or modules that were removed
- Dead internal links

### Verification Process

1. Read each documentation file from the inventory
2. For each verifiable claim, compare against the code inventory
3. For items in the code inventory with no doc coverage, flag as undocumented
4. For items in docs with no code inventory match, verify absence with
   Grep/Glob before flagging as stale
5. Record each result:
   - **Match**: Doc accurately reflects code — no finding needed
   - **Mismatch**: Doc contradicts code — typically Critical, but use judgment
   - **Partial**: Doc is incomplete or imprecise — typically Low, but Medium
     or higher if the gap affects a user-facing API or procedure
   - **Undocumented**: Code feature not in docs — typically High, but Medium
     for internal-only features or Low for minor config options
   - **Stale**: Doc references removed functionality — typically High, but
     Critical if users would follow broken instructions

### Record Findings

Follow the template at `templates/findings-code-check.md`. Write to
`artifacts/findings-code-check.md`.

Each finding must include:

- **Severity**: Critical, High, Medium, or Low (use the guidance in the
  verification process above, but assess each finding individually)
- **Dimension**: Accuracy, Completeness, or Staleness
- **File**: Doc file path and line (e.g., `README.md:85`)
- **Code location**: Source file and line
- **Documented claim**: What the docs say (direct quote)
- **Actual behavior**: What the code does
- **Evidence**: Code snippet in a fenced code block with language tag
- **Fix**: Correction, if known with high confidence (omit if unsure)

## Output

- `artifacts/findings-code-check.md`

## When This Phase Is Done

Report to the user:

- Total findings by type (mismatch, partial, undocumented, stale)
- Inventory coverage (which agents ran, items found per category)
- Top 3 most critical findings

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.

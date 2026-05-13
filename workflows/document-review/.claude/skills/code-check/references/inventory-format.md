# Inventory Fragment Format

You MUST produce your output in exactly this format. The orchestrator parses
this to merge fragments from all discovery agents.

## [Category Name]

### Items

For each discovered item, produce one entry:

- **`ITEM_NAME`**
  - Type: env-var | cli-flag | config-field | endpoint | data-model |
    file-path | external-dep | build-target
  - Source: `path/to/file.go:42` (exact file and line where the item is
    defined or consumed)
  - Default: `"value"` (if discoverable, otherwise omit this line)
  - Required: yes | no | unknown
  - Description: (extracted from code comments, help text, or inferred from
    context)
  - Workflow: installation | usage | both

### Confidence Notes

List any ambiguous or uncertain findings here. Do NOT include them as items
above.

- "Found reference to X but could not confirm it is user-facing"
- "Y appears in test code only — excluded"

## Rules

- Only list items you have HIGH confidence are real. Precision over recall.
- Exclude test-only items unless they appear in documentation.
- Exclude vendored/generated code (`vendor/`, `node_modules/`, generated
  files).
- Use the env var name as the canonical ITEM_NAME when the item is an
  environment variable.
- Workflow tagging heuristics:
  - `installation` — item appears in deployment manifests, Dockerfiles, CI
    configs, setup scripts, Makefiles, Kustomize/Helm configs; consumed only
    at build/deploy time
  - `usage` — item is read at runtime in application code
  - `both` — item appears in both installation and runtime contexts
  - When unclear, default to `both`

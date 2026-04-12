# RHOAI Manager

Comprehensive workflow for managing the complete lifecycle of Red Hat OpenShift AI (RHOAI) and Open Data Hub (ODH): installation, updates, version detection, and uninstallation.

## Overview

This workflow provides an AI-powered pipeline for:
- Installing RHOAI or ODH from scratch on OpenShift clusters
- Updating RHOAI or ODH to latest nightly builds
- Detecting RHOAI version and build information
- Completely uninstalling RHOAI or ODH when needed
- Managing cluster connections and authentication
- Safely switching between RHOAI and ODH

## Important: RHOAI and ODH Cannot Coexist

RHOAI and ODH share cluster-scoped CRDs (`DataScienceCluster`, `DSCInitialization`) and overlapping operators. They **cannot** be installed on the same cluster simultaneously. Both `/rhoai-install` and `/odh-install` detect the other and block with a clear error.

## Structure

```
workflows/rhoai-manager/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   └── commands/
│       ├── oc-login.md           # OpenShift cluster login
│       ├── rhoai-install.md      # RHOAI installation
│       ├── rhoai-version.md      # RHOAI version detection
│       ├── rhoai-update.md       # RHOAI update to latest nightly
│       ├── rhoai-uninstall.md    # RHOAI uninstall
│       ├── odh-install.md        # ODH installation
│       ├── odh-update.md         # ODH update to latest nightly
│       ├── odh-uninstall.md      # ODH uninstall
│       ├── odh-pr-tracker.md     # Track ODH PRs in RHOAI builds
│       └── mirror-images.md     # Mirror images to disconnected bastions
└── README.md                     # This file
```

## Commands

### /oc-login

Login to OpenShift cluster using credentials from Ambient session.

**Usage:** `/oc-login`

**Required env vars:** `OCP_SERVER`, `OCP_USERNAME`, `OCP_PASSWORD`

---

### /rhoai-install

Install RHOAI from scratch on an OpenShift cluster.

**Usage:**
```bash
/rhoai-install                                    # Latest dev nightly (default)
/rhoai-install channel=stable-3.4                 # GA stable-3.4 channel
/rhoai-install catalog=redhat-operators           # GA production catalog
```

**Prerequisite:** No existing RHOAI **or ODH** installation (detected automatically).

**What gets deployed:**
- Operator namespace: `redhat-ods-operator`
- Application namespace: `redhat-ods-applications`
- DataScienceCluster with all components

---

### /rhoai-update

Update RHOAI to the latest nightly or GA build.

**Usage:**
```bash
/rhoai-update                    # Pull latest (preserves current channel)
/rhoai-update 3.4 -c stable-3.4  # Update with explicit channel
```

**Features:** Preserves channel, auto-detects newer component images, forces reinstall if needed.

---

### /rhoai-version

Check installed RHOAI version, CSV, catalog digest, and all component image SHAs.

**Usage:** `/rhoai-version`

---

### /rhoai-uninstall

Completely uninstall RHOAI from an OpenShift cluster.

**Usage:**
```bash
/rhoai-uninstall              # Remove everything (use this before installing ODH)
/rhoai-uninstall graceful     # Graceful then forceful cleanup
/rhoai-uninstall keep-crds    # Keep CRDs
/rhoai-uninstall keep-all     # Keep CRDs and user resources
```

---

### /odh-install

Install Open Data Hub (ODH) nightly on an OpenShift cluster.

**Usage:**
```bash
/odh-install                  # odh-stable-nightly catalog, fast channel (default)
/odh-install channel=fast image=quay.io/opendatahub/opendatahub-operator-catalog:latest
```

**Prerequisite:** No existing ODH **or RHOAI** installation (detected automatically).

**Key differences from RHOAI:**

| | RHOAI | ODH |
|-|-------|-----|
| Package | `rhods-operator` | `opendatahub-operator` |
| Operator namespace | `redhat-ods-operator` | `openshift-operators` |
| App namespace | `redhat-ods-applications` | `opendatahub` |
| Default channel | `stable-3.4` / `beta` | `fast` |
| Nightly tag | `rhoai-3.4` (floating) | `odh-stable-nightly` (floating) |

---

### /odh-update

Update ODH to the latest nightly build.

**Usage:**
```bash
/odh-update                   # Pull latest odh-stable-nightly
/odh-update image=quay.io/opendatahub/opendatahub-operator-catalog:latest
```

**Note:** ODH nightlies typically bump the CSV version daily, so OLM auto-upgrades without a forced reinstall in most cases.

---

### /odh-uninstall

Completely uninstall ODH from an OpenShift cluster.

**Usage:**
```bash
/odh-uninstall              # Remove everything (use this before installing RHOAI)
/odh-uninstall keep-crds    # Keep CRDs
/odh-uninstall keep-all     # Keep CRDs and user resources
```

**Note:** Use the default (no flags) when switching to RHOAI — `keep-crds` or `keep-all` would leave conflicting CRDs.

---

### /odh-pr-tracker

Track whether an ODH pull request has been included in the latest RHOAI build.

**Usage:** `/odh-pr-tracker <pr-number>`

---

### /mirror-images

Mirror all RHOAI operator and component images from a connected cluster to both disconnected cluster bastion registries.

**Usage:** `/mirror-images`

**What it does:**

1. Extracts images from connected cluster's CSV relatedImages + running pods
2. Builds a combined pull secret with source registry and bastion credentials
3. Deploys a mirror pod on the connected cluster (fast AWS-internal transfers)
4. Mirrors all images to both bastions with `--keep-manifest-list=true --filter-by-os=".*"`
5. Tags destinations with `:latest` to prevent Quay tagless manifest GC
6. Verifies every image on both bastions, reports failures

**Required inputs:** Both bastion addresses, bastion credentials, RHOAI version, optional exclude patterns.

---

## Typical Workflows

### Fresh RHOAI Installation
```
1. /oc-login
2. /rhoai-install
3. /rhoai-version
```

### Fresh ODH Installation
```
1. /oc-login
2. /odh-install
3. /rhoai-version   # (check via version command — ODH has no dedicated version command yet)
```

### Pull Latest Nightly (RHOAI)
```
1. /oc-login
2. /rhoai-update
3. /rhoai-version
```

### Pull Latest Nightly (ODH)
```
1. /oc-login
2. /odh-update
```

### Switch from RHOAI to ODH
```
1. /oc-login
2. /rhoai-uninstall          # Standard uninstall (removes CRDs)
3. /odh-install
```

### Switch from ODH to RHOAI
```
1. /oc-login
2. /odh-uninstall            # Standard uninstall (removes CRDs)
3. /rhoai-install
```

### Mirror Images to Disconnected Clusters
```
1. /oc-login           # Connect to the connected cluster
2. /mirror-images      # Mirror all RHOAI images to both bastions
```

### Decommission
```
1. /oc-login
2. /rhoai-uninstall   # or /odh-uninstall
```

## Prerequisites

- OpenShift cluster (version 4.12+)
- `oc` CLI installed (auto-installed if missing)
- Cluster credentials configured in Ambient session:
  - `OCP_SERVER` - OpenShift cluster API URL
  - `OCP_USERNAME` - Your OpenShift username
  - `OCP_PASSWORD` - Your OpenShift password
- Cluster admin permissions

## Output Artifacts

All artifacts are stored in `artifacts/rhoai-manager/`:

- `reports/*.md` - Installation and update reports
- `version/*.md` - Version detection summaries
- `logs/*.log` - Detailed execution logs

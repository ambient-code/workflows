# /index - Build semantic indexes for documentation

## Purpose

Build a semantic summary of each documentation folder so future discovery
runs can skip irrelevant folders instead of grepping all files.

## Prerequisites

- Access to the documentation location (repo or subfolder)
- Write permissions to create `.doc-index/` in the docs location

## When to use

- The docs location has many folders and you plan to run the workflow
  multiple times
- You want faster discovery in future sessions

## Important

Indexes are only worth building if you commit and push them. Without
that, they're lost when the session ends and the next run starts from
scratch.

## Process

1. Ask the user where the documentation lives:
   - Same repo, subfolder (ask which folder)
   - Separate repo (ask for URL or local path)
2. Check if `.doc-index/manifest.json` already exists
   - If yes: for each folder in the manifest, compute SHA256 hashes of
     all doc files and compare against the hashes stored in the manifest.
     Only rebuild folders where at least one file hash differs. Report
     which folders are up-to-date and which need rebuilding
   - If no: build indexes for all folders from scratch
3. Scan the docs location for folders containing documentation files
   - Add any newly discovered folders (not present in the manifest) to
     the rebuild list
   - Remove entries for folders that no longer exist
4. For folders with subfolders, create sub-indexes per subfolder
5. Dispatch a subagent to build the indexes
6. Generate a semantic summary for each folder covering: what it
   documents, what code changes would affect it, key technical concepts
7. Write indexes to `.doc-index/` and update `manifest.json`. The
   manifest MUST store per-file SHA256 hashes (not just file counts)
   so that future runs can detect exactly which folders changed:

   ```json
   {
     "version": "1.0",
     "updated": "<ISO 8601>",
     "folders": {
       "<folder-name>": {
         "built": "<ISO 8601>",
         "doc_hashes": {
           "<folder>/<file>.md": "<sha256>",
           "<folder>/<file2>.md": "<sha256>"
         }
       }
     }
   }
   ```

8. Ask where to commit the indexes (current branch or main)

## Output

- `.doc-index/manifest.json` — metadata with per-file SHA256 hashes
- `.doc-index/<folder-name>.index.md` — semantic summary per folder

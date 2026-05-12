# /index - Build semantic indexes for documentation

Build a semantic summary of each documentation folder so future discovery
runs can skip irrelevant folders instead of grepping all files.

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
2. Check if `.doc-index/` already exists with a `manifest.json`
   - If yes: compare file hashes against the manifest and only rebuild
     folders where files have changed. Report which folders are up to
     date and which need rebuilding
   - If no: build indexes for all folders from scratch
3. Scan the docs location for folders containing documentation files
4. For folders with subfolders, create sub-indexes per subfolder
5. Dispatch a subagent to build the indexes
6. Generate a semantic summary for each folder covering: what it
   documents, what code changes would affect it, key technical concepts
7. Write indexes to `.doc-index/` and update the manifest with current
   file hashes
8. Ask where to commit the indexes (current branch or main)

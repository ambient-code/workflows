---
description: List all data sources that informed the PRD creation, including documents, code references, research, and external sources.
displayName: prd.sources
icon: 📚
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command generates a comprehensive list of all data sources that informed the PRD creation. It analyzes the PRD document, discovery artifacts, requirements, and any referenced materials to create a complete source attribution list.

1. **Load Context**:
   - Read `prd.md` (required)
   - Read `discovery.md` (if exists)
   - Read `rfe.md` (if exists)
   - Read `prd-review-report.md` (if exists)
   - Scan for any references, citations, or links in these documents

2. **Identify Source Types**:

   ### Google Drive / Google Workspace Sources
   - Documents accessed via Google Drive MCP server
   - Google Docs referenced or linked
   - Google Sheets referenced or linked
   - Google Slides referenced or linked
   - Any Google Workspace files mentioned in the PRD or discovery

   ### UXR MCP Sources
   - User research reports accessed via UXR MCP
   - Research studies from "All UXR Reports" folder
   - User research findings cited in the PRD
   - Research data referenced in requirements

   ### Code Repository Sources
   - Code repositories referenced
   - GitHub/GitLab links mentioned
   - Code examples or snippets referenced
   - API documentation referenced
   - Technical specifications from codebase

   ### User-Uploaded Files
   - Files directly uploaded by the user
   - Documents provided during discovery or requirements phases
   - Images, diagrams, or mockups uploaded
   - Any attachments or uploaded materials

   ### External Web Sources
   - Competitor websites referenced
   - Industry reports or articles
   - Documentation sites (e.g., API docs, technical specs)
   - Research papers or academic sources
   - Blog posts or articles referenced
   - Standards or specifications (e.g., WCAG, RFCs)

   ### Internal Documentation
   - Internal wiki pages
   - Previous PRDs or Features referenced
   - Design documents or specifications
   - Architecture documents
   - Process documentation

3. **Extract Source Information**:

   For each source identified, extract:
   - **Source Type**: Document, Code Repository, Website, Research Study, etc.
   - **Source Name/Title**: The name or title of the source
   - **Location/URL**: Where the source can be found (link, path, folder)
   - **Access Method**: How it was accessed (Google Drive MCP, UXR MCP, direct upload, web search, etc.)
   - **Relevance**: What part of the PRD it informed (e.g., "User Research - Pain Points", "Technical Architecture", "Competitive Analysis")
   - **Citation**: How it's referenced in the PRD (if applicable)

4. **Generate Sources Document**: Create `prd-sources.md`:

   ```markdown
   # PRD Data Sources

   **PRD Document**: prd.md
   **Generated**: [Current Date]
   **Total Sources**: [Count]

   This document lists all data sources that informed the creation of the Product Requirements Document.

   ## Source Summary

   | Source Type | Count |
   |-------------|-------|
   | Google Drive Documents | X |
   | UXR Research Reports | X |
   | Code Repositories | X |
   | User-Uploaded Files | X |
   | External Websites | X |
   | Internal Documentation | X |

   ## Sources by Category

   ### Google Drive / Google Workspace

   #### [Document Name]
   - **Type**: Google Doc/Sheet/Slide
   - **Location**: [Google Drive path or link]
   - **Accessed Via**: Google Drive MCP
   - **Relevance**: [What part of PRD it informed]
   - **Citation**: [How referenced in PRD, if applicable]
   - **Date Accessed**: [If available]

   ### UXR Research Reports

   #### [Research Study Name]
   - **Type**: User Research Report
   - **Location**: UXR MCP - "All UXR Reports" folder
   - **Accessed Via**: UXR MCP Server
   - **Relevance**: [What part of PRD it informed, e.g., "User Pain Points", "Feature Requirements"]
   - **Citation**: [How referenced in PRD, if applicable]
   - **Key Insights**: [Brief summary of how it informed the PRD]

   ### Code Repositories

   #### [Repository Name]
   - **Type**: Code Repository
   - **Location**: [GitHub/GitLab URL or path]
   - **Accessed Via**: [Code access method]
   - **Relevance**: [What part of PRD it informed, e.g., "Technical Architecture", "API Design"]
   - **Files Referenced**: [Specific files or directories if mentioned]
   - **Citation**: [How referenced in PRD, if applicable]

   ### User-Uploaded Files

   #### [File Name]
   - **Type**: [Document, Image, Diagram, etc.]
   - **Location**: User-uploaded file
   - **Accessed Via**: Direct upload
   - **Relevance**: [What part of PRD it informed]
   - **Citation**: [How referenced in PRD, if applicable]

   ### External Websites

   #### [Website/Page Name]
   - **Type**: Website / Documentation / Article
   - **URL**: [Full URL]
   - **Accessed Via**: Web search / Direct reference
   - **Relevance**: [What part of PRD it informed, e.g., "Competitive Analysis", "Industry Standards"]
   - **Citation**: [How referenced in PRD, if applicable]
   - **Date Accessed**: [If available]

   ### Internal Documentation

   #### [Document Name]
   - **Type**: Internal Document
   - **Location**: [Path or link]
   - **Accessed Via**: [Access method]
   - **Relevance**: [What part of PRD it informed]
   - **Citation**: [How referenced in PRD, if applicable]

   ## Sources by PRD Section

   ### Executive Summary
   - [List sources that informed this section]

   ### Problem Statement
   - [List sources that informed this section]

   ### User Research
   - [List sources that informed this section]

   ### Competitive Analysis
   - [List sources that informed this section]

   ### Technical Considerations
   - [List sources that informed this section]

   ### Requirements
   - [List sources that informed this section]

   ## Source Attribution

   This PRD was informed by:
   - X user research studies
   - X internal documents
   - X external references
   - X code repositories
   - X competitor analyses

   All sources have been cited where applicable in the PRD document itself.
   ```

5. **Search for References**:

   - Scan PRD text for:
     - URLs and links
     - File paths
     - Document names
     - Research study citations
     - Code repository references
     - "According to..." or "Based on..." statements
     - Citation markers (e.g., "[1]", "(Source, 2024)")
   
   - Check discovery and requirements documents for:
     - Source materials mentioned
     - References to external documents
     - Links to research or documentation

6. **Verify Source Accessibility**:

   - For Google Drive sources: Verify they're accessible via Google Drive MCP
   - For UXR sources: Verify they're in the "All UXR Reports" folder
   - For code repositories: Verify links are valid
   - For external websites: Note if links are still accessible
   - For uploaded files: Note if files are still available

7. **Generate Attribution Summary**:

   - Count sources by type
   - Identify most influential sources
   - Note any missing or inaccessible sources
   - Highlight research-backed requirements

8. **Report Completion**:

   - Path to sources document
   - Summary of source types found
   - Total number of sources
   - Any sources that couldn't be verified

## Guidelines

- **Comprehensive**: Include ALL sources, even if indirectly referenced
- **Specific**: Provide exact names, URLs, or paths when available
- **Attribution**: Link sources to specific PRD sections they informed
- **Verification**: Note if sources are still accessible
- **Transparency**: Be clear about how each source was accessed
- **Citations**: Include how sources are cited in the PRD (if applicable)

## Source Detection Methods

1. **Explicit Citations**: Look for citation markers, "Source:", "Reference:", etc.
2. **Links**: Extract all URLs and links from documents
3. **File References**: Look for file names, document titles, or paths
4. **Context Clues**: Identify sources from "According to...", "Based on...", "Research shows..."
5. **Agent Activity**: Note which MCP servers or tools were used (Google Drive, UXR, etc.)
6. **Upload History**: Check for any files that were uploaded during the workflow

## Missing Sources

If a source is referenced but cannot be located:
- Note it in the sources document
- Indicate what information it was supposed to provide
- Suggest how to locate or verify the source

## Usage Notes

- Run this command after PRD creation to document all sources
- Useful for:
  - Audit trails
  - Compliance requirements
  - Source verification
  - Understanding PRD foundations
  - Reproducing research-backed decisions
- Can be run multiple times as PRD evolves
- Sources document can be shared with stakeholders for transparency


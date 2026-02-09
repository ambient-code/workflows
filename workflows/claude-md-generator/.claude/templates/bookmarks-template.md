# Bookmarks

Progressive disclosure for task-specific documentation and references.

## Table of Contents
{{#each categories}}
- [{{name}}](#{{anchor}})
{{/each}}

---

{{#each categories}}
## {{name}}

{{#each links}}
### [{{title}}]({{url}})

{{description}}

**Added by**: {{added_by}} | **Date**: {{date_added}}{{#if comment}} | **Note**: {{comment}}{{/if}}

{{/each}}

{{/each}}

---

**Tip**: Use `/bookmark <url> <description>` in Ambient to add to this list collaboratively with your team.

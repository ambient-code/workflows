# {{project_name}}

{{description}} Built with {{tech_stack}}.

## Structure

{{#each directories}}
- `{{path}}` - {{purpose}}
{{/each}}

## Key Files

{{#each key_files}}
- {{description}}: `{{file}}{{#if line_range}}:{{line_range}}{{/if}}`
{{/each}}

## Commands

```bash
{{build_command}}  # {{build_description}}
{{test_command}}   # {{test_description}}
{{#if lint_command}}
{{lint_command}}   # {{lint_description}}
{{/if}}
```

{{#if has_bookmarks}}
## More Info

See [BOOKMARKS.md](BOOKMARKS.md) for {{bookmarks_description}}.
{{/if}}

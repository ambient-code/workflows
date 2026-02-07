# Claude Config - {{user_name}}

{{role}} focused on {{focus_area}}.

## Active Projects

{{#each projects}}
- [{{name}}]({{url}})
{{/each}}

{{#if communication_prefs}}
## Communication

{{#each communication_prefs}}
- {{this}}
{{/each}}
{{/if}}

{{#if has_bookmarks}}
## References

See [BOOKMARKS.md](BOOKMARKS.md) for {{bookmarks_description}}.
{{/if}}

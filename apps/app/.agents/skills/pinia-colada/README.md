# Pinia Colada Skill - User Guide

A Claude skill for building production-grade async data flows in Vue 3 applications using Pinia Colada.

## What This Skill Does

This skill helps you implement queries, mutations, cache management, and optimistic updates with Pinia Colada. Claude becomes a specialist in:

- Query and mutation patterns
- Key factory design
- Cache invalidation strategies
- Optimistic updates
- Pagination
- TypeScript integration
- Debugging async state issues

## When to Use This Skill

Use this skill when you need help with:

- **Setting up queries** — fetching data with proper loading/error states
- **Creating mutations** — updating server data with cache invalidation
- **Key management** — designing dependency-aware cache keys
- **Optimistic UIs** — showing immediate feedback before server confirms
- **Pagination** — handling multi-page data with smooth transitions
- **Debugging** — fixing stale data, race conditions, or invalidation issues

## How to Activate

The skill activates automatically when you mention Pinia Colada in your request, or you can explicitly reference it:

```
"Using the Pinia Colada skill, help me implement a product listing with search and pagination"
```

## Common Use Cases

### Searchable Lists
Perfect for implementing search with debouncing and pagination while keeping previous results visible during fetch.

### Detail Pages
Load single-item data with proper loading states, background refetching, and cache coordination with list views.

### Forms with Server Sync
Handle form submissions, optimistic updates, validation errors, and cache invalidation.

### Real-time Features
Polling, manual refresh, and invalidation strategies for keeping data fresh.

## Tips for Best Results

1. **Be specific about your feature** — "product search with filters" vs "make a query"
2. **Mention existing code** — "I already have a productService with getAll()"
3. **Share your API shape** — show request/response types if available
4. **Ask about trade-offs** — "Should I use optimistic updates here?"

## Anti-Patterns Claude Will Warn You About

- ❌ Putting queries inside Pinia stores
- ❌ Static keys for dynamic queries
- ❌ Using `useQueryCache()` outside Vue setup
- ❌ Over-invalidating the cache
- ❌ Not handling race conditions in optimistic updates

## Troubleshooting Guide

The skill includes a troubleshooting matrix for common issues:

- Query not refetching on changes → key dependencies
- Invalidation not working → key hierarchy
- Stale data showing → expected behavior vs bugs
- Optimistic rollback failures → race conditions

## Integration with Other Tools

This skill works alongside:

- **Vue 3** — composables, reactivity, TypeScript
- **TypeScript** — full type safety
- **Vue Router** — route params in keys
- **Existing APIs** — any HTTP client (axios, fetch, etc.)

## Need Help?

Ask Claude:
- "Explain why you chose this pattern"
- "What are the alternatives?"
- "How does this handle [edge case]?"
- "Can you refactor this to be more maintainable?"

**Ready to build?** Ask Claude anything about Pinia Colada and this skill will guide you through production-quality async data management.

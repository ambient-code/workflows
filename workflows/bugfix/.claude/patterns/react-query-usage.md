# React Query Usage Patterns

This document provides proven patterns for implementing React Query in bug fixes and features.

## Table of Contents

1. [Basic Query](#pattern-1-basic-query)
2. [Mutation with Invalidation](#pattern-2-mutation-with-invalidation)
3. [Dependent Queries](#pattern-3-dependent-queries)
4. [Infinite Queries](#pattern-4-infinite-queries)
5. [Polling Until Condition Met](#pattern-5-polling-until-condition-met)
6. [Polling with Pagination](#pattern-6-polling-with-pagination)
7. [Optimistic Updates](#pattern-7-optimistic-updates)

---

## Pattern 1: Basic Query

**Use when**: Fetching data that should be cached and automatically refetched.

```typescript
import { useQuery } from '@tanstack/react-query';

function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
}
```

**Key points**:
- `queryKey` should be an array that uniquely identifies the query
- `staleTime` controls when data is considered stale
- `gcTime` controls when unused data is garbage collected

---

## Pattern 2: Mutation with Invalidation

**Use when**: Updating data and refreshing dependent queries.

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: UpdateUserRequest) => updateUser(userData),
    onSuccess: (data, variables) => {
      // Invalidate and refetch user queries
      queryClient.invalidateQueries({ queryKey: ['user', variables.userId] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
    onError: (error) => {
      console.error('Failed to update user:', error);
    },
  });
}
```

**Key points**:
- Use `invalidateQueries` to mark queries as stale
- Pass specific query keys to avoid invalidating unrelated data
- Handle errors in `onError` callback

---

## Pattern 3: Dependent Queries

**Use when**: A query depends on data from another query.

```typescript
function useUserPosts(userId: string | undefined) {
  return useQuery({
    queryKey: ['posts', userId],
    queryFn: () => fetchUserPosts(userId!),
    enabled: !!userId, // Only run when userId is available
  });
}

function Component() {
  const { data: user } = useUser();
  const { data: posts } = useUserPosts(user?.id);

  // ...
}
```

**Key points**:
- Use `enabled` option to conditionally run queries
- Query won't execute until `enabled` is `true`

---

## Pattern 4: Infinite Queries

**Use when**: Implementing infinite scroll or load-more functionality.

```typescript
import { useInfiniteQuery } from '@tanstack/react-query';

function useInfinitePosts() {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite'],
    queryFn: ({ pageParam = 1 }) => fetchPosts(pageParam),
    getNextPageParam: (lastPage, pages) => {
      return lastPage.hasMore ? lastPage.nextPage : undefined;
    },
    initialPageParam: 1,
  });
}
```

**Key points**:
- `getNextPageParam` determines if there are more pages
- Return `undefined` when no more pages available
- Access data via `query.data.pages`

---

## Pattern 5: Polling Until Condition Met

**Use when**: Continuously fetching data until a terminal state is reached.

```typescript
import { useQuery } from '@tanstack/react-query';

interface Task {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

function useTask(taskId: string) {
  return useQuery({
    queryKey: ['task', taskId],
    queryFn: () => fetchTask(taskId),
    refetchInterval: (query) => {
      const task = query.state.data as Task | undefined;

      // Stop polling when terminal state reached
      if (!task) return false;
      if (task.status === 'completed' || task.status === 'failed') {
        return false;
      }

      // Poll every 2 seconds while pending/running
      return 2000;
    },
  });
}
```

**Key points**:
- `refetchInterval` can be a function that returns a number or `false`
- Return `false` to stop polling
- Return a number (milliseconds) to continue polling at that interval
- Check `query.state.data` for current data

**Session-specific terminal states**:

When polling for session status, use these terminal phases:
- `Stopped`: Session was stopped by user
- `Completed`: Session finished successfully
- `Failed`: Session failed with error
- `Error`: Session encountered an error state

Example:

```typescript
refetchInterval: (query) => {
  const session = query.state.data as Session | undefined;
  if (!session) return false;

  // Explicitly check all terminal phases
  const terminalPhases = ['Stopped', 'Completed', 'Failed', 'Error'];
  if (terminalPhases.includes(session.phase)) {
    return false;
  }

  return 2000; // Poll every 2 seconds
}
```

---

## Pattern 6: Polling with Pagination

**Use when**: Polling data that uses pagination (e.g., polling a paginated list for status updates).

### The Challenge

When combining `refetchInterval` with `placeholderData: keepPreviousData`, you must account for the fact that `query.state.data` may contain **previous page data** while a new page is loading.

### The Pattern

```typescript
import { useQuery } from '@tanstack/react-query';

interface Session {
  id: string;
  phase: 'Running' | 'Stopped' | 'Completed' | 'Failed' | 'Error';
}

interface PaginatedSessions {
  sessions: Session[];
  total: number;
  page: number;
}

function useSessionsPaginated(page: number) {
  return useQuery({
    queryKey: ['sessions', page],
    queryFn: () => fetchSessions({ page }),
    placeholderData: keepPreviousData, // Keeps previous page while loading next
    refetchInterval: (query) => {
      // CRITICAL: When using keepPreviousData, query.state.data may contain
      // the PREVIOUS page's data while a new page is loading.

      // Option 1: Check isFetching to avoid stale data
      // Only make polling decisions when NOT transitioning between pages
      if (query.state.isFetching) {
        // We're currently fetching new data, don't change polling behavior
        // based on potentially stale data
        return query.state.fetchStatus === 'fetching' ? 2000 : false;
      }

      const data = query.state.data as PaginatedSessions | undefined;
      if (!data) return false;

      // Check if ANY session in current page is in a transitional state
      const hasTransitionalSessions = data.sessions.some(session => {
        const terminalPhases = ['Stopped', 'Completed', 'Failed', 'Error'];
        return !terminalPhases.includes(session.phase);
      });

      // Poll if there are transitional sessions, otherwise stop
      return hasTransitionalSessions ? 2000 : false;
    },
  });
}
```

### Key Points

1. **`placeholderData: keepPreviousData` interaction**:
   - While navigating between pages, `query.state.data` contains the **previous page's data**
   - This can cause polling decisions based on stale data
   - Example: User views page 1 (has running sessions) → navigates to page 2 (all completed) → during transition, polling logic sees page 1 data and continues polling

2. **Check `query.state.isFetching`**:
   - When `isFetching` is `true`, you're in a page transition
   - Avoid making polling decisions based on `query.state.data` during transitions
   - Alternative: maintain current polling state during transitions

3. **Complete terminal state list**:
   - Always explicitly list ALL terminal phases
   - For sessions: `['Stopped', 'Completed', 'Failed', 'Error']`
   - Don't rely on implicit fallbacks (makes code unclear)

4. **Pagination-aware polling logic**:
   ```typescript
   // ✅ GOOD: Accounts for pagination transitions
   refetchInterval: (query) => {
     if (query.state.isFetching) {
       // Maintain current polling during page transitions
       return 2000;
     }
     const data = query.state.data;
     return shouldPoll(data) ? 2000 : false;
   }

   // ❌ BAD: Ignores pagination, uses stale data
   refetchInterval: (query) => {
     const data = query.state.data;
     return shouldPoll(data) ? 2000 : false;
   }
   ```

### Alternative Approach: Use Query Key in Logic

```typescript
refetchInterval: (query) => {
  // Extract current page from query key
  const queryKey = query.queryKey as ['sessions', number];
  const currentPage = queryKey[1];

  const data = query.state.data as PaginatedSessions | undefined;

  // Verify data matches current page before making decisions
  if (data && data.page === currentPage) {
    const hasTransitionalSessions = data.sessions.some(/* ... */);
    return hasTransitionalSessions ? 2000 : false;
  }

  // Data doesn't match current page, maintain current state
  return 2000;
}
```

---

## Pattern 7: Optimistic Updates

**Use when**: Providing instant feedback before server confirmation.

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function useToggleTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleTodo,
    onMutate: async (todoId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['todos'] });

      // Snapshot previous value
      const previousTodos = queryClient.getQueryData(['todos']);

      // Optimistically update
      queryClient.setQueryData(['todos'], (old: Todo[]) =>
        old.map(todo =>
          todo.id === todoId ? { ...todo, completed: !todo.completed } : todo
        )
      );

      // Return context for rollback
      return { previousTodos };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousTodos) {
        queryClient.setQueryData(['todos'], context.previousTodos);
      }
    },
    onSettled: () => {
      // Refetch after mutation completes
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}
```

**Key points**:
- Cancel in-flight queries in `onMutate`
- Save previous state for rollback
- Restore previous state in `onError`
- Refetch in `onSettled` to sync with server

---

## Common Pitfalls

### 1. Not using query keys correctly

```typescript
// ❌ BAD: Same key for different data
useQuery({ queryKey: ['user'], queryFn: () => fetchUser(userId) });

// ✅ GOOD: Include parameters in key
useQuery({ queryKey: ['user', userId], queryFn: () => fetchUser(userId) });
```

### 2. Over-polling

```typescript
// ❌ BAD: Polling without checking if needed
refetchInterval: 1000,

// ✅ GOOD: Conditional polling
refetchInterval: (query) => {
  const needsPolling = checkIfNeedsPolling(query.state.data);
  return needsPolling ? 2000 : false;
}
```

### 3. Ignoring pagination state with polling

```typescript
// ❌ BAD: Polling with pagination, ignoring keepPreviousData
refetchInterval: (query) => {
  const data = query.state.data;
  return shouldPoll(data) ? 2000 : false;
}

// ✅ GOOD: Account for keepPreviousData behavior
refetchInterval: (query) => {
  if (query.state.isFetching) return 2000;
  const data = query.state.data;
  return shouldPoll(data) ? 2000 : false;
}
```

### 4. Incomplete terminal state checks

```typescript
// ❌ BAD: Missing 'Error' phase
if (session.phase === 'Stopped' || session.phase === 'Completed' || session.phase === 'Failed') {
  return false;
}

// ✅ GOOD: Explicit complete list
const terminalPhases = ['Stopped', 'Completed', 'Failed', 'Error'];
if (terminalPhases.includes(session.phase)) {
  return false;
}
```

---

## When to Use Each Pattern

| Scenario | Pattern |
|----------|---------|
| Simple data fetch | Pattern 1: Basic Query |
| Creating/updating data | Pattern 2: Mutation with Invalidation |
| Query needs result from another query | Pattern 3: Dependent Queries |
| Load more / infinite scroll | Pattern 4: Infinite Queries |
| Waiting for task completion | Pattern 5: Polling Until Condition Met |
| Polling a paginated list | Pattern 6: Polling with Pagination |
| Instant UI feedback | Pattern 7: Optimistic Updates |

---

## Additional Resources

- [React Query Documentation](https://tanstack.com/query/latest)
- [Query Keys Documentation](https://tanstack.com/query/latest/docs/react/guides/query-keys)
- [Pagination Guide](https://tanstack.com/query/latest/docs/react/guides/paginated-queries)

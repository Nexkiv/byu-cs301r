### [High] Unvalidated `sort`/`order_by` used directly in SQL `ORDER BY`

**File:** `test-app/models/note.py:43-49, 54-57` and `test-app/models/user.py:62-66`

**Vulnerable Code:**
```
query = (
    f"SELECT * FROM notes WHERE user_id = ? "
    f"AND (title LIKE ? OR content LIKE ?) "
    f"ORDER BY {sort_by}"
)
...
query = (
    f"SELECT * FROM notes "
    f"WHERE title LIKE ? OR content LIKE ? "
    f"ORDER BY {sort_by}"
)
```
and
```
order = filters.get("order_by", "created_at")
query = f"SELECT id, username, role, created_at FROM users WHERE {where} ORDER BY {order}"
```

**Explanation:** The `ORDER BY` clause is constructed with an f-string inserting user-controllable `sort_by` or `order` values directly into SQL; while parameterization is used for values, the ordering column/expr is not validated. An attacker can inject SQL expressions into the ordering clause to manipulate the query or attempt data exfiltration depending on the DB's behavior.

**Proposed Refactor:** Whitelist allowed sort columns and map incoming `sort`/`order_by` values to safe column names; never interpolate raw user input into SQL.
```
ALLOWED_SORTS = {"created_at": "created_at", "title": "title", "id": "id"}
sort_col = ALLOWED_SORTS.get(sort_by, "created_at")
query = (
    "SELECT * FROM notes WHERE user_id = ? "
    "AND (title LIKE ? OR content LIKE ?) "
    "ORDER BY " + sort_col
)
```
For the user filter: validate `order` similarly before concatenation.
```
order_col = ALLOWED_USER_ORDERS.get(filters.get('order_by', ''), 'created_at')
query = f"SELECT id, username, role, created_at FROM users WHERE {where} ORDER BY {order_col}"
```

**Rationale:** Restricting to known column names prevents arbitrary SQL expression injection while preserving sorting capabilities.

---

### [Low] No evidence of raw shell/command invocation found

**File:** N/A

**Vulnerable Code:** N/A

**Explanation:** I inspected the code paths reachable from HTTP entry points and found no usage of `subprocess`, `os.system`, or template rendering that interpolates user-supplied templates. The primary injection concern is the SQL ordering interpolation above.

**Proposed Refactor:** Continue to avoid shell invocations; when needed, use parameterized APIs and validated inputs.


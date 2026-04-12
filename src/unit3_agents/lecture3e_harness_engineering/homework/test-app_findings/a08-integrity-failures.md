### [Critical] Insecure deserialization via `pickle.loads()` on client-supplied blob

**File:** `test-app/utils/export.py:25-36`

**Vulnerable Code:**
```
def import_preferences(user_id, blob):
    prefs = pickle.loads(blob)
    ...
    db.execute(
        "INSERT OR REPLACE INTO user_preferences (user_id, data) VALUES (?, ?)",
        (user_id, pickle.dumps(prefs)),
    )
```

**Explanation:** The function deserializes an arbitrary binary blob from the client using `pickle.loads()`. `pickle` is not safe for untrusted input — it can execute arbitrary code during deserialization, leading to remote code execution (RCE) if an attacker can supply crafted blobs.

**Proposed Refactor:** Avoid `pickle` for data interchange with clients. Use a safe, structured serialization format such as JSON or a restricted parser (e.g., `json` with schema validation). If arbitrary Python objects must be serialized, use a server-side-only store and never accept raw pickled data from clients.

```
# Example: expect JSON preferences
import json

def import_preferences(user_id, blob):
    prefs = json.loads(blob)
    # validate prefs structure
    db.execute(..., (user_id, json.dumps(prefs)))
```

**Rationale:** JSON (or another safe serialization format) prevents arbitrary code execution during parsing and makes stored preference schemas explicit and auditable.


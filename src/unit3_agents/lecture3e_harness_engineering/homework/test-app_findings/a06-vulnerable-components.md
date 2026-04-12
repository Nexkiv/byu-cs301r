### [High] Missing dependency manifest prevents component vulnerability review

**File:** repository root (no `requirements.txt` / `pyproject.toml` found)

**Vulnerable Code:** N/A — absence of manifest

**Explanation:** There is no visible `requirements.txt`, `pyproject.toml`, or `Pipfile` in the project root. Without pinned dependency versions, it's not possible to determine whether installed packages contain known CVEs or to reproduce a secure environment.

**Proposed Refactor:** Add a `requirements.txt` (or `pyproject.toml` + lock file) with explicit version pins and use a dependency scanning workflow (e.g., `pip-audit`, Dependabot) in CI to catch known vulnerabilities.

```
pip freeze > requirements.txt
# or use poetry/poetry.lock or pip-tools to pin deps
```

**Rationale:** Pinning dependencies and scanning them ensures known vulnerable packages are identified and can be upgraded.

---

### [Medium] Audit surface (known crypto & web libs) - need versions

**File:** code imports in `test-app` (e.g., `flask`, `cryptography`, `werkzeug`) (see `findings/recon.md`) 

**Vulnerable Code:** N/A — informational

**Explanation:** The code imports security-sensitive libraries (`flask`, `cryptography`, `werkzeug`), but without version information we cannot determine if any specific CVEs apply.

**Proposed Refactor:** Add a pinned manifest and run a dependency scanner as part of CI, then remediate any flagged packages.


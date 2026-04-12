---
name: Auditors
description: Shared guidelines, severity rubric, and output format for all OWASP auditor skills
---

These are shared guidelines for all auditor skills. Apply these guidelines
when executing an auditor skill — these guidelines alone are not an action step.

## Before You Begin

Read `findings/recon.md` to understand the codebase structure, entry points,
and data flows before starting your analysis.

## How to Analyze

For each finding:

1. Identify the vulnerable code — include the file path, line number, and a code snippet.
2. Explain the vulnerability — what the flaw is and how it could be exploited.
3. Classify the severity using the rubric below.
4. Propose a refactoring solution — not a bolt-on fix, but a structural change
   that corrects the flaw while preserving functionality. Include a code example
   of the refactored approach.

## Severity Classification

- **Critical** — Exploitable without authentication or special access, leads to
  full system compromise, data breach, or remote code execution.
- **High** — Exploitable with minimal effort or low-privilege access, leads to
  significant data exposure or privilege escalation.
- **Medium** — Requires specific conditions or authenticated access to exploit,
  leads to limited data exposure or partial system impact.
- **Low** — Theoretical or difficult to exploit in practice, minimal impact if exploited.

## Output Format

Write your findings to the file specified by your auditor skill.
Use this format for each finding:

### [Severity] Finding title

**File:** `path/to/file.py:42`

**Vulnerable Code:**
```
code snippet here
```

**Explanation:** What the flaw is and how it could be exploited.

**Proposed Refactor:**
```
refactored code here
```

**Rationale:** Why this refactor resolves the issue without hurting functionality.

---

If you find no issues in your category, write a file that states no issues were
found and briefly explain what you checked.

## Scope

Analyze only your assigned OWASP category. If you encounter a potential issue in
a different category, add it to a `## Deferred to Other Auditors` section at the
bottom of your file with the file path and suspected category — then move on.

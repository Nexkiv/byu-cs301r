# Harness Engineering Session Summary

## Objective

Build a general-purpose OWASP Top 10 security audit team using `myteam` that can be pointed at any codebase and produce a structured compliance report with actionable refactoring solutions. The team was designed for use with OpenAI Codex.

## What We Built

### Team Structure

```
AGENTS.md                              -- Codex entrypoint
.myteam/
  role.md                              -- Coordinator (orchestrates workflow)
  recon/skill.md                       -- Maps codebase structure and entry points
  auditors/skill.md                    -- Shared guidelines, severity rubric, output format (context only)
  auditors/broken-access-control/      -- A01
  auditors/crypto-failures/            -- A02
  auditors/injection/                  -- A03
  auditors/insecure-design/            -- A04
  auditors/security-misconfiguration/  -- A05
  auditors/vulnerable-components/      -- A06
  auditors/auth-failures/              -- A07
  auditors/integrity-failures/         -- A08
  auditors/logging-monitoring/         -- A09
  auditors/ssrf/                       -- A10
  catch-all/skill.md                   -- Mechanical gap check (recon vs auditor coverage)
  reporter/skill.md                    -- Compiles final report
```

### Workflow

1. Coordinator loads `recon` -- maps the target codebase to `findings/recon.md`
2. Coordinator loads `auditors` -- shared guidelines enter conversation context (no action taken)
3. Coordinator loads each auditor skill sequentially -- each writes to its own file in `findings/`
4. Coordinator loads `catch-all` -- mechanically compares recon concerns against auditor findings
5. Coordinator loads `reporter` -- compiles everything into `findings/final-report.md`

### Key Design Decisions

**File-based handoff over conversation memory.** Each skill writes its output to a specific file in `findings/`. Auditors read `findings/recon.md` for context. The reporter reads all files to compile the report. This keeps token usage controlled and prevents context window bloat.

**Shared guidelines loaded as context, not as an agent.** The parent `auditors/skill.md` contains the severity rubric, output format, and shared rules. It explicitly states it is not an action step. The coordinator loads it before any specialist, so its content is in the conversation when specialists execute.

**Constructive scope boundaries instead of "do not" statements.** Rather than telling agents what not to do, each skill gives agents a constructive action for out-of-scope observations: "add it to a Deferred to Other Auditors section with the file path and suspected category -- then move on."

**Mechanical catch-all instead of analytical.** The catch-all skill compares file paths only -- no code analysis, no risk assessment. It lists recon entries whose file paths don't appear in any auditor's findings. This prevents scope creep while surfacing coverage gaps.

## Test Codebase

We built two versions of a Flask + SQLite test application in `test-app/`:

**Version 1 (simple):** 4 files with obvious vulnerabilities -- string-concatenated SQL everywhere, plaintext password logging in error responses, hardcoded secrets, no auth on admin routes, direct path traversal.

**Version 2 (realistic):** 15 files across 4 modules (`auth/`, `api/`, `models/`, `utils/`) with buried vulnerabilities mixed alongside properly-written code:

- A01: Auth bypass via `_test_bypass` query param backdoor, IDOR on `/notes/export`, path traversal via `dir` param on download, missing `@admin_required` on `/admin/stats`
- A02: AES-ECB mode for note encryption, predictable PRNG for password reset tokens
- A03: ORDER BY injection in `search_notes` and `find_users_by_filter` (hidden behind otherwise-parameterized queries)
- A05: Traceback leak in global error handler, CORS wildcard `*`
- A07: Legacy MD5 password compat path, password logging on failed login, fallback SECRET_KEY, defined but unenforced rate limit, 365-day remember-me session
- A08: `pickle.loads()` on client-supplied preference blobs
- A09: Plaintext passwords in log output

## Model Comparison

We ran the full audit team against the realistic test app with three OpenAI models.

### gpt-5.4 (3-auditor run, A01/A03/A07 only)

**Grade: A**

- 11/11 vulnerabilities found in target categories
- Perfect lane discipline -- no overreach, clean deferrals
- Production-ready refactors with complete code examples
- Excellent recon with file paths and line numbers throughout
- Correctly identified `pickle.loads` in Unaddressed Concerns
- Missed 3 other-category vulnerabilities (AES-ECB, traceback leak, CORS) -- expected since those auditors didn't exist yet

### gpt-5-mini (full 10-auditor run)

**Grade: B+**

- Found all major buried vulnerabilities including the auth backdoor, IDOR, path traversal, both ORDER BY injections, AES-ECB, predictable PRNG, and pickle deserialization
- Full workflow completed with no tool errors (including catch-all and final report)
- Only miss: `/admin/stats` missing auth (Low severity)
- Minor cross-auditor duplication (password logging in both A07 and A09)
- Good refactors with rationale, slightly less polished than gpt-5.4
- Catch-all produced some noise from non-concern recon entries
- Cost: ~$1.10/$4.40 per 1M tokens

### gpt-4.1-mini (full 10-auditor run)

**Grade: D+**

- Missed all 4 A01 vulnerabilities (including the critical auth backdoor)
- Multiple lane violations (CORS flagged by A01, pickle flagged by A04)
- False positive on correctly-secured admin routes
- 3+ duplicate findings across auditors
- Shallow recon with no line numbers crippled downstream auditors
- Generic refactors ("add rate limiting") without actual code
- Tool environment errors: invented ripgrep flags, tried nonexistent `myteam run` command, shell syntax failures in Codex sandbox
- Workflow incomplete -- no final report or uncovered-concerns file generated

### Comparison Table

| Metric                | gpt-5.4    | gpt-5-mini | gpt-4.1-mini |
|-----------------------|------------|------------|--------------|
| Recon quality         | A+         | A-         | C            |
| A01 detection         | 4/4        | 3/4        | 0/4          |
| A03 detection         | 2/2        | 2/2        | 1/2          |
| A07 detection         | 5/5        | 3/5*       | 3/5          |
| Lane discipline       | Perfect    | Minor overlaps | Multiple violations |
| False positives       | 0          | 0          | 1            |
| Refactor quality      | Production | Good       | Generic      |
| Workflow completion   | Full       | Full       | Partial      |

*2 A07 items correctly covered by other auditors (A02, A05)

## Key Findings on Harness Engineering

1. **Recon quality determines everything downstream.** When gpt-4.1-mini produced shallow recon without file paths, every auditor suffered. The recon skill is the foundation -- if it fails, the whole system degrades.

2. **File-based handoff works.** Writing to specific files in `findings/` kept context clean, prevented token bloat, and gave each skill a concrete deliverable. It also made auditor output independently reviewable.

3. **Positive instructions outperform prohibitions.** "Add out-of-scope observations to a Deferred section" worked better than "do not analyze other categories." Agents need somewhere constructive to put observations.

4. **Shared context as a non-action skill works when loaded before specialists.** Since `myteam get skill auditors/injection` doesn't inherit from `auditors/skill.md` automatically, the coordinator must load the parent first. This keeps shared guidelines in one place.

5. **The model matters more for tool use than for analysis.** gpt-4.1-mini's failures weren't primarily analytical -- it invented shell commands and ripgrep flags that don't exist. A model that can't operate in its environment can't follow even well-structured instructions.

6. **gpt-5-mini is the cost-effective sweet spot.** At roughly 1/5 the cost of gpt-5.4, it delivered ~90% of the detection quality with zero tool errors and full workflow completion. The one miss was the lowest-severity finding.

7. **Mechanical catch-all is better than analytical.** Giving a catch-all skill analytical freedom would invite overreach. A simple file-path comparison surfaces coverage gaps without re-analyzing code.

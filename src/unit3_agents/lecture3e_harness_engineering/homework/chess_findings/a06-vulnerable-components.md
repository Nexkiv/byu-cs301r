### [Medium] Dependencies require vulnerability scanning and pinning verification

**Files reviewed:** `chess/pom.xml`, `chess/server/pom.xml` (dependencies and versions logged)

**Observed dependencies and versions:**
- `com.google.code.gson:gson:2.10.1` (chess/pom.xml)
- `com.sparkjava:spark-core:2.9.3` (chess/server/pom.xml)
- `mysql:mysql-connector-java:8.0.30` (chess/server/pom.xml)
- `org.mindrot:jbcrypt:0.4` (chess/server/pom.xml)
- `org.slf4j:slf4j-simple:1.7.36` (chess/server/pom.xml)

**Explanation:**
- The codebase declares explicit versions in Maven POMs, which is good for reproducible builds. However, dependency versions may contain known CVEs that change over time.

**Proposed Action:**
- Run an automated dependency vulnerability scanner (e.g., `mvn dependency:tree` then `mvn -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -X` with OS tooling or use Snyk/OSS Index/Dependabot) to check for known CVEs affecting the above versions.
- Regularly update dependencies and test for breaking changes. If production security requirements exist, consider using a dependency policy that blocks known-severity CVEs.

**Rationale:**
- Vulnerabilities in third-party libraries are a common attack vector. Automated continuous scanning ensures quick detection and remediation of known issues.


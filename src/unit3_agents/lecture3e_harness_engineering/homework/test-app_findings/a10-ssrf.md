No SSRF issues identified.

I searched the code paths reachable from HTTP entry points and found no uses of `requests`, `urllib`, `http.client`, or other HTTP client libraries that take user-supplied URLs. If future code adds outbound-request endpoints, re-check inputs and apply allowlisting and host validation.


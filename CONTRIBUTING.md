# Contributing

Issues and pull requests are welcome for parser bugs, safer defaults, and clearer novice wording.

## Rules

- Scan only in tests against `127.0.0.1` or fixtures.
- Do not add credential attacks, exploit payloads, or default secrets.
- Keep the API on localhost unless the operator opts in.
- New plugins should use argument-list subprocesses or in-process checks — never `shell=True`.

Security reports: **catflap55.GIT@proton.me** (see SECURITY.md).

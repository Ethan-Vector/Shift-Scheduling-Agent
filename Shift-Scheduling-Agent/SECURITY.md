# Security

This repository is a reference implementation and is **not** hardened for hostile multi-tenant environments.

## Reporting
If you discover a vulnerability, please open a private report (or disclose responsibly).

## Design notes
- The CLI writes only to `workspace/` unless you explicitly pass a different output path.
- The "agent" is offline and does not execute arbitrary code.
- Tool calls are allowlisted and validated.


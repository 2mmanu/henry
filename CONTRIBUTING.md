# Contributing to HEnRY

Thank you for helping make governed agent systems easier to build and audit.

## Before you start

- Search existing issues and discussions before proposing duplicate work.
- Open an issue for architectural changes, new contracts or security-sensitive behavior.
- Keep changes focused and preserve domain sovereignty, least privilege and traceability.
- Never commit credentials, runtime state, personal data or proprietary domain context.

## Development setup

HEnRY requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
make install-dev
make check
```

Run the development control plane with `HENRY_RUNTIME=demo make run`.

## Pull requests

1. Add or update tests for behavior changes.
2. Update contracts and architecture documentation together.
3. Explain security, context visibility and audit implications.
4. Keep public APIs backward compatible or document the breaking change.
5. Ensure `make check` succeeds.

By contributing, you agree that your contributions are licensed under Apache-2.0.

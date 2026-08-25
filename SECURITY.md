# Security Policy

## Supported versions

HEnRY is currently alpha software. Security fixes are applied to the latest revision of the main
development branch; no long-term support release exists yet.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub private vulnerability
reporting when enabled, or contact the maintainers privately through the repository owner.

Include affected versions, reproduction steps, impact, prerequisites and any proposed mitigation.
Avoid including real credentials or personal data. Maintainers will acknowledge a complete report,
coordinate remediation and credit reporters who wish to be named.

## Security boundaries

The default in-memory stores, development API-key identity adapter and demo runtime are not
production controls. Production deployments must use durable tenant-isolated storage, workload or
OIDC identity, secret management, transport encryption and centrally managed policy.

# Browser Security

## CSP
Explicitly resolve Content Security Policy including script/style/connect/frame sources and third-party script exceptions.

## CORS
Credentialed requests require exact allowed origins; wildcard origins with credentials are forbidden. Resolve preflight and headers.

## CSRF
Cookie credentials require an explicit CSRF defense such as strict SameSite plus verified Origin/anti-CSRF token as project-resolved. Bearer-only designs must document why CSRF is not applicable.

## XSS
Use framework-safe rendering, avoid untrusted HTML sinks, encode/sanitize intentionally, and test injection paths.

## Clickjacking
Resolve frame-ancestors/X-Frame-Options posture.

## Referrer Policy
Choose a referrer policy appropriate to sensitive routes.

## Permissions Policy
Disable unnecessary browser capabilities and document required exceptions.

## Open Redirects
Validate redirect destinations against an allowlisted/local policy.

## Service Worker and private caching
Service worker/offline caches must not persist private authenticated data unless the project explicitly defines a secure cache lifecycle. Private API responses require explicit cache-control behavior.

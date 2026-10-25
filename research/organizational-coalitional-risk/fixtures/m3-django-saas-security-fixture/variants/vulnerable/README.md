<div align="center">

**English** · [Русский](README.ru.md)

</div>

# Django Multi-Tenant SaaS Starter

A production-grade starting point for a multi-tenant B2B SaaS on **Django 5 + Django REST Framework**. It ships with **row-level tenancy**, **role-based access control (RBAC)**, an **invitation flow**, **JWT auth**, and a tested guarantee that one tenant can never read or write another tenant's data.

Runs anywhere on **sqlite** out of the box (so the test suite is reproducible on any machine); switches to **Postgres** in production with a single `DATABASE_URL`.

---

## Why this exists

Most "SaaS boilerplates" either skip tenancy entirely or bolt it on as a `tenant_id` you have to remember to filter by — which is exactly how cross-tenant data leaks happen. This starter makes isolation the **default** at the ORM layer: the tenant-scoped manager fails *closed*, and crossing tenants requires an explicit, auditable opt-out. The interesting engineering is in the tenancy model and its tradeoffs, discussed honestly below.

## Features

- **Row-level tenancy** — a `Tenant` (organization) boundary, a tenant-scoped base model, and a manager that auto-filters every query to the active tenant.
- **RBAC** — `Membership` links a `User` to a `Tenant` with a role (`owner` / `admin` / `member`). DRF permission classes gate actions by role.
- **Invitations** — invite by email → pending `Invitation` → accept → `Membership`. Tokenized, expiring, owner/admin-only to send.
- **JWT auth** — `djangorestframework-simplejwt`. Registration atomically creates a user, a tenant, and an **owner** membership.
- **Clean settings** — `base / dev / test / prod`, env-driven (`django-environ`), `DATABASE_URL` support, security hardening in prod.
- **Containerized** — `Dockerfile` + `docker-compose.yml` (web + Postgres + Redis) for prod-like running.
- **CI** — GitHub Actions running `ruff` + `pytest` on Python 3.10 and 3.12.

## Architecture

```
config/
  settings/          base.py · dev.py · test.py · prod.py
  urls.py · wsgi.py · asgi.py
apps/
  common/            tenancy machinery (the core)
    tenant_context.py  ContextVar holding the active tenant (thread/async-safe)
    models.py          TimeStampedModel, TenantManager, TenantScopedModel
    permissions.py     HasActiveTenant, IsTenantMember/Admin/Owner
  accounts/          custom User (email login) + registration
  tenants/           Tenant, Membership (RBAC), Invitation, middleware, API
  projects/          Project — the sample tenant-scoped resource
tests/               isolation · RBAC · auth/registration · invitations
```

### How a request resolves its tenant

1. **`TenantMiddleware`** resolves the active tenant from, in order: the `X-Tenant` header (matches `Tenant.slug`), the request subdomain (`acme.example.com`), or — for session users — the user's sole membership. It binds that tenant into a `ContextVar`.
2. The **`TenantManager`** on every tenant-scoped model reads that `ContextVar` and filters `get_queryset()` to the active tenant. With no tenant bound, it returns **nothing** (fail-closed), not everything.
3. **`TenantScopedModel.save()`** stamps the active tenant onto new rows automatically, so application code never sets `tenant` by hand and can't get it wrong.
4. **RBAC** is enforced by DRF permission classes that resolve the caller's `Membership` in the active tenant and check the role.

> **One subtlety worth calling out (it's a real interview question):** Django middleware runs *before* DRF authenticates the request, so under JWT `request.user` is still anonymous at middleware time. The middleware therefore resolves only the *tenant* (header/subdomain are user-independent); the caller's *membership* is resolved lazily in the permission layer once DRF has authenticated the user. See `apps/tenants/utils.py`.

### Tenancy model: row-level vs schema-based — the honest tradeoffs

This starter uses **row-level (shared-schema) tenancy**: every tenant's rows live in the same tables, discriminated by a `tenant_id` foreign key. The main alternatives are **schema-per-tenant** (one Postgres schema each, e.g. `django-tenants`) and **database-per-tenant**.

**Why row-level here:**

- **It runs and tests anywhere.** Schema- and database-per-tenant need Postgres and schema-switching plumbing; row-level works on sqlite, so the whole suite is reproducible with zero infrastructure — which is the point of a *starter*.
- **Cheap, fast onboarding.** Creating a tenant is a single `INSERT`, not a `CREATE SCHEMA` + migrate. Thousands of small tenants stay cheap.
- **Cross-tenant analytics are trivial** — they're just queries without the tenant filter (via the explicit unscoped manager).
- **One migration set.** Schema migrations run once, not once-per-tenant.

**What you give up (and how this starter mitigates it):**

- **Isolation is enforced in application code, not by the database.** A forgotten `.filter(tenant=...)` is a data leak. *Mitigation:* the scoped manager is the **default** and fails closed; crossing tenants is an explicit `all_tenants` / `unscoped()` call; isolation is covered by tests. For defense-in-depth on Postgres you can additionally enable **Row-Level Security (RLS)** policies.
- **The "noisy neighbor" problem.** One tenant's heavy queries share the same tables/indexes as everyone else. *Mitigation:* good composite indexes leading with `tenant_id`; connection pooling; per-tenant rate limits.
- **Per-tenant operations are coupled.** You can't trivially restore, export, or relocate a single tenant the way database-per-tenant allows.
- **Weaker blast radius for compliance.** Some regulated/enterprise customers contractually require physical data separation.

**When to graduate:** start row-level; move large or compliance-sensitive tenants to **schema- or database-per-tenant** (a hybrid: most tenants share a schema, a few VIPs get their own). The `tenant_context` abstraction is deliberately the only place that "knows" how the current tenant is selected, so swapping resolution strategies later touches one module, not the whole codebase.

## Quickstart

```bash
# 1. Environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # optional for dev

# 2. Database (sqlite by default)
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin

# 3. Run
python manage.py runserver
```

Run the test suite:

```bash
pytest
```

Lint:

```bash
ruff check .
```

## API overview

Base path: `/api/v1/`. All resource endpoints require a JWT (`Authorization: Bearer <token>`) and, except where noted, an active tenant via the `X-Tenant: <slug>` header.

| Method | Path | Auth | Tenant header | Notes |
| --- | --- | --- | --- | --- |
| `POST` | `/auth/register/` | none | no | Creates user + tenant + **owner** membership; returns JWTs |
| `POST` | `/auth/token/` | none | no | Obtain access/refresh tokens (`email` + `password`) |
| `POST` | `/auth/token/refresh/` | none | no | Refresh an access token |
| `GET` | `/tenants/` | JWT | no | The tenants you belong to (with your role) |
| `PATCH` | `/tenants/{id}/` | JWT | yes | Update a tenant — owner/admin only |
| `GET` | `/members/` | JWT | yes | Members of the active tenant |
| `PATCH`/`DELETE` | `/members/{id}/` | JWT | yes | Manage members — owner/admin only; owner protected |
| `GET` | `/invitations/` | JWT | yes | Pending/issued invitations |
| `POST` | `/invitations/` | JWT | yes | Invite by email — owner/admin only |
| `POST` | `/invitations/accept/` | JWT | no | Accept an invite by `token` (token identifies the tenant) |
| `GET`/`POST` | `/projects/` | JWT | yes | List/create projects (any member) |
| `GET`/`PATCH` | `/projects/{id}/` | JWT | yes | Retrieve/update a project (any member) |
| `DELETE` | `/projects/{id}/` | JWT | yes | Delete a project — owner/admin only |

`GET /healthz/` is an unauthenticated health check.

### Example flow

```bash
# Register — creates the "Acme" tenant and makes you its owner
curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"founder@acme.io","password":"Sup3r-Secret-pw!","tenant_name":"Acme"}'
# -> { "access": "...", "tenant": { "slug": "acme", "role": "owner" }, ... }

ACCESS=...   # paste the access token

# Create a project in Acme
curl -s -X POST http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer $ACCESS" -H 'X-Tenant: acme' \
  -H 'Content-Type: application/json' -d '{"name":"Website redesign"}'

# Invite a teammate (owner/admin only)
curl -s -X POST http://localhost:8000/api/v1/invitations/ \
  -H "Authorization: Bearer $ACCESS" -H 'X-Tenant: acme' \
  -H 'Content-Type: application/json' -d '{"email":"teammate@acme.io","role":"member"}'
```

## Testing & the isolation guarantee

The suite (`tests/`, pytest + pytest-django) is the proof that tenancy works, not just a claim:

- **`tests/test_tenant_isolation.py`** — tenant A's queryset never returns B's rows (ORM *and* API); A gets `404` (not `200`) when fetching B's object by id; A cannot mutate B's object; the manager fails closed when no tenant is bound; saves are stamped with the caller's tenant.
- **`tests/test_rbac.py`** — a member can read but cannot delete a project or send invitations (`403`); owner/admin can; a member of A has no rights in B.
- **`tests/test_auth_registration.py`** — registration creates an **owner** membership and returns a usable JWT; duplicate email rejected; unauthenticated access is `401`.
- **`tests/test_invitations.py`** — full invite → accept → membership flow; access is granted only *after* acceptance; wrong-email and expired-token accepts are rejected; duplicate pending invites are rejected.

## Deployment notes

- **Settings:** set `DJANGO_SETTINGS_MODULE=config.settings.prod`. Required env: `SECRET_KEY`, `DATABASE_URL` (Postgres DSN), `ALLOWED_HOSTS`. Optional: `REDIS_URL`, `SECURE_SSL_REDIRECT`, JWT lifetimes.
- **Database:** point `DATABASE_URL` at Postgres, e.g. `postgres://user:pw@host:5432/db`. No code changes — `dj-database-url` handles the switch.
- **Static files:** WhiteNoise serves compressed, hashed static assets; `collectstatic` runs in the Docker build.
- **Containers:** `docker compose up --build` brings up web + Postgres + Redis. The web image migrates on start and serves via Gunicorn.
- **Migrations in prod:** prefer a dedicated release step (`python manage.py migrate`) over the convenience entrypoint.
- **Hardening (prod settings):** HSTS, secure cookies, SSL redirect, and `SECURE_PROXY_SSL_HEADER` are enabled; tune via env.

## Tech stack

Django 5 · Django REST Framework · djangorestframework-simplejwt · django-environ · dj-database-url · WhiteNoise · Gunicorn · psycopg 3 · pytest / pytest-django · ruff.

## License

[MIT](LICENSE) © 2026 Maxim Chumakov

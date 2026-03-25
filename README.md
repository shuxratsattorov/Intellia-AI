# Intellia AI — API

Feature-based (modules)

## Tech stack
- Python (FastAPI)
- Async SQLAlchemy + Alembic migrations
- Auth: JWT, RS256, Argon2id + HMAS sold, RBAC
- Redis (cache / rate limit)
- Docker

## Project structure (feature-based modules)

```text
INTELLIA APP/
├─ app/
│  ├─ main.py                       # create_app + router include
│  ├─ asgi.py                       # prod entry
│  ├─ __init__.py
│  │
│  ├─ core/                         # cross-cutting
│  │  ├─ config.py                  # env/settings
│  │  ├─ logging.py                 # structured logging
│  │  ├─ middleware.py              # cors, request-id, rate limit hooks
│  │  ├─ errors.py                  # exception handlers
│  │  ├─ security.py                # jwt, password hash
│  │  ├─ observability.py           # metrics/tracing hooks
│  │  ├─ constants.py
│  │  └─ deps.py                    # common dependencies (db, current_user)
│  │
│  ├─ db/
│  │  ├─ base.py                    # SQLAlchemy DeclarativeBase
│  │  ├─ session.py                 # async engine + AsyncSessionLocal
│  │  ├─ migrations/                # alembic + versions
│  │  └─ health.py                  # DB ping util
│  │
│  ├─ integrations/                 # external services
│  │  ├─ ai/                        # LLM provider adapters (OpenAI, etc.)
│  │  │  ├─ client.py
│  │  │  ├─ prompts/                # prompt templates (short, versioned)
│  │  │  └─ safety.py               # content filters (policy)
│  │  ├─ storage/                   # S3/local storage (exports)
│  │  ├─ mail/                      # forgot password emails
│  │  └─ cache/                     # Redis cache (rate limit, sessions)
│  │
│  ├─ shared/                       # reusable building blocks (NOT business)
│  │  ├─ pagination.py
│  │  ├─ responses.py
│  │  ├─ id.py                      # uuid/ulid helpers
│  │  ├─ time.py
│  │  └─ validators.py
│  │
│  ├─ modules/                      # modules
│  │  ├─ auth/
│  │  │  ├─ api.py                  # /auth routes: login/register/logout/forgot/reset
│  │  │  ├─ schemas.py              # request/response DTO
│  │  │  ├─ service.py              # business logic
│  │  │  ├─ repository.py           # db access
│  │  │  ├─ models.py               # UserCredentials / ResetToken tables
│  │  │  └─ deps.py                 # auth-specific deps
│  │  │
│  │  ├─ users/
│  │  │  ├─ api.py                  # profile endpoints
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py              # edit profile, preferences (theme)
│  │  │  ├─ repository.py
│  │  │  └─ models.py
│  │  │
│  │  ├─ notifications/
│  │  │  ├─ api.py                  # list/mark read/unread count
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py
│  │  │  ├─ repository.py
│  │  │  └─ models.py
│  │  │
│  │  ├─ projects/
│  │  │  ├─ api.py                  # my projects / recent / archive
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py
│  │  │  ├─ repository.py
│  │  │  └─ models.py               # Project table
│  │  │
│  │  ├─ documents/
│  │  │  ├─ api.py                  # create/edit/save docs
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py              # editor actions (bold, headings, etc.)
│  │  │  ├─ repository.py
│  │  │  └─ models.py               # Document, DocumentVersion
│  │  │
│  │  ├─ ai_generator/
│  │  │  ├─ api.py                  # generate/regenerate/summarize/replace synonyms
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py              # orchestration with LLM, prompt selection
│  │  │  ├─ repository.py           # generation history
│  │  │  └─ models.py               # GenerationJob, PromptVersion
│  │  │
│  │  ├─ exports/
│  │  │  ├─ api.py                  # export DOCX/PDF/PPTX
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py              # conversion pipeline
│  │  │  └─ models.py               # ExportTask metadata
│  │  │
│  │  ├─ billing/
│  │  │  ├─ api.py                  # pricing, subscriptions (if needed)
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py
│  │  │  ├─ repository.py
│  │  │  └─ models.py
│  │  │
│  │  └─ health/
│  │     ├─ api.py                  # /health
│  │     └─ schemas.py
│  │
│  ├─ api/
│  │  ├─ router.py                  # include all module routers
│  │  └─ v1.py                      # /api/v1 prefix
│  │
│  └─ tests/
│     ├─ conftest.py                # db fixtures, async client
│     ├─ unit/                      # service tests
│     └─ integration/               # api/db tests
│
├─ pyproject.toml
├─ alembic.ini
├─ Dockerfile
└─ .env.example
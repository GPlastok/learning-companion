# Guides

A tutorial series about this project. It explains how the code was built and what each piece of Django does, using the real code from the repo.

Read it in order the first time. Each chapter builds on the one before.

| # | Chapter | You learn |
|---|---|---|
| 1 | [The pipeline](01-the-pipeline.md) | How a GitHub issue becomes tested, reviewed code |
| 2 | [The project skeleton](02-the-project-skeleton.md) | Projects, apps, settings, the Makefile |
| 3 | [The custom user](03-the-custom-user.md) | `AbstractUser`, `AUTH_USER_MODEL`, migrations |
| 4 | [Models and relationships](04-models-and-relationships.md) | Fields, foreign keys, one-to-one, many-to-many, signals, data migrations |
| 5 | [URLs, views and templates](05-urls-views-templates.md) | How a request travels through Django |
| 6 | [Forms](06-forms.md) | Validation, `clean_<field>`, model forms |
| 7 | [Logging in with email](07-login-with-email.md) | Authentication backends |
| 8 | [Permissions and deleting an account](08-permissions-and-deletion.md) | 403 vs 404, logout, cascades |
| 9 | [The admin](09-the-admin.md) | Django's built-in back office |
| 10 | [Testing with pytest-django](10-testing.md) | Fixtures, the test client, red and green |
| 11 | [What the reviews caught](11-what-the-reviews-caught.md) | Real bugs, and why each one mattered |

## How to use these guides

Every chapter ends with **Try it yourself**. Do those steps. Reading code is good; changing it and watching what breaks is better.

Most commands need the virtual environment and your `.env` file, which you already have. Two commands come up often:

```bash
make dev                              # start the site at http://127.0.0.1:8000
.venv/bin/python manage.py shell      # a Python prompt with Django loaded
```

When a chapter says "D7" or "AC13", it points to a decision or an acceptance criterion in [the #3 plan](../plans/feature-authentication-and-profile-management-plan.md). You don't need to read the plan, but it's there if you want the full reasoning.

## What's covered so far

- Ticket #1: the project setup.
- Ticket #3: authentication and profiles.

Later tickets (goals, resources, the AI summary, the dashboard) can get their own chapters as they're built.

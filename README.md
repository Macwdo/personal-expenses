# Pingou o que?

Umbrella workspace for the Pingou o que? product. This repo coordinates the
child app repositories through Git submodules; implementation code lives in the
children.

## Child Repositories

- `pingou-o-que-frontend`: authenticated Next.js product UI, including routes,
  components, table workflows, hooks, and API client wrappers.
- `pingou-o-que-backend`: Django/DRF API for financial organization, backed by
  PostgreSQL and organized around models, serializers, selectors, services,
  views, migrations, seed data, and tests.
- `pingou-o-que-landing-page`: public marketing site for the product, built with
  Next.js and shadcn-style components.

## Working Model

Use the parent repository for cross-repo planning and submodule pointer updates.
Use the child repositories for app implementation, app-specific OpenSpec
artifacts, tests, and validation.

For app-only work:

```bash
cd /home/macwdo/Codes/pingou-o-que/pingou-o-que-frontend
mires-aiw create change/example
```

For multi-app work:

```bash
cd /home/macwdo/Codes/pingou-o-que
mires-aiw workspace list --folder .
mires-aiw workspace create change/example --folder . pingou-o-que-frontend pingou-o-que-backend
```


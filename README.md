# vbos-backend

[![Docker](https://github.com/Vanuatu-National-Statistics-Office/vbos-backend/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Vanuatu-National-Statistics-Office/vbos-backend/actions/workflows/docker-publish.yml)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

VBOS Django application and data services. Check out the project's [documentation](https://vanuatu-national-statistics-office.github.io/vbos-backend/).

# Prerequisites

- [Docker Engine](https://docs.docker.com/engine/install)
- [Docker Compose](https://docs.docker.com/compose/install)

# Local Development

Start the dev server for local development:

```bash
cd deploy/
docker compose up
```

Run a command inside the docker container:

```bash
docker compose run --rm web [command]
```

# Configuration

Copy the `.env.example` file to `.env` and edit the variables you need to configure the access to the DigitalOcean Spaces (S3 compatible).

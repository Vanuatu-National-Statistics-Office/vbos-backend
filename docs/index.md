# vbos-backend

[![Django CI](https://github.com/Vanuatu-National-Statistics-Office/vbos-backend/actions/workflows/test.yml/badge.svg)](https://github.com/Vanuatu-National-Statistics-Office/vbos-backend/actions/workflows/test.yml)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

VBOS Django application and data services.
Check out the project's [source code](https://github.com/Vanuatu-National-Statistics-Office/vbos-backend/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Initialize the project

Start the dev server for local development:

```bash
docker-compose up
```

Create a superuser to login to the admin:

```bash
docker-compose run --rm web ./manage.py createsuperuser
```

FROM ghcr.io/developmentseed/titiler:latest

COPY deploy/tiler/app.py app.py

ENV MODULE_NAME=app
ENV VARIABLE_NAME=app
ENV HOST=0.0.0.0
ENV PORT=8001
ENV WEB_CONCURRENCY=1
CMD gunicorn -k uvicorn.workers.UvicornWorker ${MODULE_NAME}:${VARIABLE_NAME} --bind ${HOST}:${PORT} --workers ${WEB_CONCURRENCY}

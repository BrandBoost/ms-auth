#!/bin/bash

echo "Waiting for mongodb"
while ! nc -z mongodb 27017; do
  echo "Waiting for MongoDB to be available..."
  sleep 0.1
done
echo "mongodb started"

uvicorn app.main:app --host "${FASTAPI_HOST}" --reload --port "${FASTAPI_PORT}"
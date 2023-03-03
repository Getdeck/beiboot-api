#!/bin/bash
curl -sSL https://install.python-poetry.org | python3 -
poetry config virtualenvs.create false
poetry install --directory /workspace/app

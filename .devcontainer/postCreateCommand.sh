#!/bin/bash
curl -sSL https://install.python-poetry.org | python3 -
cd /workspace/app
poetry install
cd /workspace

# beiboot-api

WIP

## development

Install dependencies:

```bash
pip install -e .
```

or

```bash
poetry export -f requirements.txt --output requirements.dev.txt --without-hashes --with dev
```

Build devcontainer:

```bash
devcontainer build --no-cache --image-name "beiboot-api:devcontainer" --workspace-folder "."
```

Start devcontainer with gefyra:

```bash
gefyra run -i beiboot-api:devcontainer -n getdeck -N beiboot-api -v $(pwd):/workspace -c "/bin/sh -c 'while sleep 1000; do :; done'" --expose localhost:8001:8000
```

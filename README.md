# beiboot-api

WIP

## development

```bash
devcontainer build --no-cache --image-name "beiboot-api:devcontainer" --workspace-folder "."
```

```bash
gefyra run -i beiboot-api:devcontainer -N beiboot-api -v $(pwd):/workspace -c "/bin/sh -c 'while sleep 1000; do :; done'" --expose localhost:8001:8000
```

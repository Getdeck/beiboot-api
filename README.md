# beiboot-api

WIP

## development

```bash
devcontainer build --no-cache --image-name "beiboot-api:devcontainer" "."
```

```bash
gefyra run -i beiboot-api:devcontainer -n beiboot-api -N beiboot-api -v $(pwd):/workspace -c "/bin/sh -c 'while sleep 1000; do :; done'" --expose localhost:8001:8000
```

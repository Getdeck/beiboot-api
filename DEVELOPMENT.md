# Getdeck Beiboot API Development

This is the Beiboot API running as a side component for the [Beiboot Operator](https://github.com/Getdeck/beiboot/blob/main/operator/DEVELOPMENT.md).
It wraps the [Beiboot Python client](https://pypi.org/project/beiboot/) ([source code](https://github.com/Getdeck/beiboot/tree/main/client)) in a REST API using [FastAPI](https://fastapi.tiangolo.com/).

## Prerequisites

To get started, you only need a Kubernetes cluster and the [Poetry](https://python-poetry.org/) environment.

### Kubernetes for local development

Basically, any Kubernetes cluster will do. The following describes a local setup using [Minikube](https://minikube.sigs.k8s.io/docs/).

Assuming you have Minikube installed, please run the following on your terminal:

1. Create a Kubernetes cluster using the Docker driver

   ```bash
   minikube start --cpus=max --memory=4000 --driver=docker --embed-certs --addons=default-storageclass storage-provisioner
   ```

   Alternatively you can use k3d:

   ```bash
   k3d cluster create getdeck-api --agents 1 -p 8080:80@agent:0 -p 31820:31820/UDP@agent:0
   ```

2. The `kubectl` context will be set automatically to this cluster (please check it anyway)
3. Create the `getdeck` namespace: `kubectl create ns getdeck`.
4. Install the Beiboot Operator to this cluster:

   ```bash
   kubectl apply -f https://raw.githubusercontent.com/Getdeck/beiboot/main/operator/manifests/beiboot.yaml
   ```

5. Store the Minikube _kubeconfig_ for later use in an application container with (working dir is _getdeck-api/app/_):

   ```bash
   kubectl config view --flatten --minify > app/beiboot_api/kubeconfig.yaml
   ```

You can delete the Minikube cluster with `minikube delete`. Please find the Minikube docs for further assistance above.

### Container-based development

#### A local container image

First you need to create a container image from the source. Please run:

```bash
docker build app/ -t getdeck-api
```

#### Gefyra

It's simple to connect Gefyra (0.13.4+) with a Kubernetes cluster.

If used together with Minikube, please follow these steps:

1. Set up Gefyra with:

   ```bash
   gefyra up --minikube
   ```

   :exclamation: If you are using a k3d cluster, omit the `--minikube` option.

2. Start a container image locally with (working dir is _getdeck-api/app/_):

   ```bash
   gefyra run -i getdeck-api -n getdeck -N getdeck-api -v $(pwd)/:/app -c "/bin/sh -c 'while sleep 1000; do :; done'" --expose localhost:8001:8000 --detach
   ```

   **Important:** Please keep in mind, that you also mount the _kubeconfig.yaml_ for the Minikube cluster. It is needed to make the application able to talk to the Kubernetes API.

3. Confirm the presence of the _kubeconfig_ file:

   ```bash
   > docker exec -it getdeck-api bash
   > du -h kubeconfig.yaml
   4.0K    kubeconfig.yaml
   ```

4. Start the fastapi process with:

   ```bash
   > docker exec -it getdeck-api bash
   > uvicorn main:app --host 0.0.0.0 --reload
   ```

5. Find the output on [http://localhost:8001](http://localhost:8001)  
   **Important:** This process is now connected to the Kubernetes API.
6. Do the development work!
7. You can remove/restart the container with:

   ```bash
   docker rm -f getdeck-api
   ```

   (build a new container image with new dependencies and start over again)

#### VSCode devcontainer

Build devcontainer:

```bash
devcontainer build --no-cache --image-name "getdeck-api:devcontainer" --workspace-folder "."
```

Start devcontainer using gefyra run:

```bash
gefyra run -i getdeck-api:devcontainer -n getdeck -N getdeck-api -v $(pwd):/workspace -c "/bin/sh -c 'while sleep 1000; do :; done'" --expose localhost:8000:8000
```

## Release

Use `bump2version`.

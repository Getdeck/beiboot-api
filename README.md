# beiboot-api

In order to use the Beiboot API, apply the provided configuration and API resources to your Beiboot Cluster:

```bash
kubectl apply -f manifests/<YOUR-SETTINGS>.yaml
```

```bash
kubectl apply -f manifests/beiboot-api.yaml
```

## Configuration

The Beiboot API can be configured using a configmap. All available option are included in the [settings.example.yaml](manifests/settings.example.yaml).

## Cluster Config Parameter

| Parameter        | Description            | Type | Default | Example                                |
| :--------------- | :--------------------- | :--- | :------ | :------------------------------------- |
| `k8s_versions`   | Supported k8s versions | List | -       | `"1.26.0,1.26.1,1.26.2,1.26.3,1.27.0"` |
| `node_count_min` | Minimum node count     | Int  | `1`     |                                        |
| `node_count_max` | Maximum node count     | Int  | `3`     |                                        |

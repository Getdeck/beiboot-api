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

| Parameter         | Description         | Default  |
| :---------------- | :------------------ | :------- |
| `k8s_version_min` | Minimum k8s version | `1.24.0` |
| `k8s_version_max` | Maximum k8s version | `None`   |
| `node_count_min`  | Minimum node count  | `1`      |
| `node_count_max`  | Maximum node count  | `3`      |

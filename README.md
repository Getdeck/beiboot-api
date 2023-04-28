# beiboot-api

In order to use the Beiboot API, apply the provided settings, configuration and API resources to your Beiboot Cluster:

```bash
kubectl apply -f manifests/<SETTINGS>.yaml
```

```bash
kubectl apply -f manifests/beiboot-api.yaml
```

## Configuration

The Beiboot API can be configured using a configmap. All available option are included in the [settings.example.yaml](manifests/settings.example.yaml).

| Parameter                  | Description              | Type | Default          | Example |
| :------------------------- | :----------------------- | :--- | :--------------- | :------ |
| `sentry_dsn`               | Sentry DNS               | Str  | -                |         |
| `sentry_environment`       | Sentry environment       | Str  | `1`              |         |
| `config_default_name`      | Default config name      | Str  | `config-default` |         |
| `config_default_namespace` | Default config namespace | Str  | `getdeck`        |         |

## Cluster Config Parameter

| Parameter        | Description            | Type | Default | Example                                |
| :--------------- | :--------------------- | :--- | :------ | :------------------------------------- |
| `k8s_versions`   | Supported k8s versions | List | -       | `"1.26.0,1.26.1,1.26.2,1.26.3,1.27.0"` |
| `node_count_min` | Minimum node count     | Int  | `1`     |                                        |
| `node_count_max` | Maximum node count     | Int  | `3`     |                                        |

Alternatively to using a ConfigMap, default cluster config parameters can be set using an `.env` file, too. In order to work, all cluster config parameters have to be prefixed with `cd_`.

```txt
cd_k8s_versions="1.26.0,1.26.1,1.26.2,1.26.3,1.27.0"
cd_node_count_min="1"
cd_node_count_max="3"
...
```

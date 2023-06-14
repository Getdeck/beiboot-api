# Getdeck API

In order to make the API available for your Host Cluster, apply the provided settings, configuration and API resources:

```bash
kubectl apply -f manifests/api-settings.yaml
```

```bash
kubectl apply -f manifests/api.yaml
```

## API Settings

The settings of the API can be configured using a `ConfigMap` (see [api-settings.example.yaml](manifests/api-settings.example.yaml)).

| Parameter                  | Description              | Type | Default   | Example |
| :------------------------- | :----------------------- | :--- | :-------- | :------ |
| `sentry_dsn`               | Sentry DNS               | Str  | -         |         |
| `sentry_environment`       | Sentry environment       | Str  | -         |         |
| `config_default_name`      | Default config name      | Str  | `default` |         |
| `config_default_namespace` | Default config namespace | Str  | `getdeck` |         |

## Groups

Currently, the API supports the following fixed groups:

- developer
- free
- (default)

Only one of the listed groups is selected based on the following priority:

`developer > free > default`

A user will be assigned to the `default` group, if no group is provided within the header.
Invalid group names are ignored.

> **_NOTE:_** We plan to extend the group system later on in order to make it more flexible, including custom groups.

## Group/Cluster Configuration

| Parameter                              | Type   | Default | Example                                | Description / Comment  |
| :------------------------------------- | :----- | :------ | :------------------------------------- | :--------------------- |
| `k8s_versions`                         | List   | -       | `"1.26.0,1.26.1,1.26.2,1.26.3,1.27.0"` | Supported k8s versions |
| `node_count_min`                       | Int    | `1`     |                                        | Minimum node count     |
| `node_count_max`                       | Int    | `3`     |                                        | Maximum node count     |
| `lifetime_limit`                       | String | `1h`    |                                        | Cluster lifetime limit |
| `session_timeout_limit`                | String | `30m`   |                                        | Session timeout limit  |
| `cluster_request_timeout_limit`        | String | `5m`    |                                        |                        |
| `server_resources_requests_cpu_min`    | String | -       |                                        |                        |
| `server_resources_requests_cpu_max`    | String | -       |                                        |                        |
| `server_resources_requests_memory_min` | String | -       |                                        |                        |
| `server_resources_requests_memory_max` | String | -       |                                        |                        |
| `server_resources_limits_cpu_min`      | String | -       |                                        |                        |
| `server_resources_limits_cpu_max`      | String | -       |                                        |                        |
| `server_resources_limits_memory_min`   | String | -       |                                        |                        |
| `server_resources_limits_memory_max`   | String | -       |                                        |                        |
| `server_resources_requests_cpu_max`    | String | -       |                                        |                        |
| `server_storage_requests_min`          | String | -       |                                        |                        |
| `server_storage_requests_max`          | String | -       |                                        |                        |
| `node_resources_requests_cpu_min`      | String | -       |                                        |                        |
| `node_resources_requests_cpu_max`      | String | -       |                                        |                        |
| `node_resources_requests_memory_min`   | String | -       |                                        |                        |
| `node_resources_requests_memory_max`   | String | -       |                                        |                        |
| `node_resources_limits_cpu_min`        | String | -       |                                        |                        |
| `node_resources_limits_cpu_max`        | String | -       |                                        |                        |
| `node_resources_limits_memory_min`     | String | -       |                                        |                        |
| `node_resources_limits_memory_max`     | String | -       |                                        |                        |
| `node_resources_requests_cpu_max`      | String | -       |                                        |                        |
| `node_storage_requests_min`            | String | -       |                                        |                        |
| `node_storage_requests_max`            | String | -       |                                        |                        |

Alternatively to using a ConfigMap, default cluster config parameters can be set using an `.env` file, too. In order to work, all cluster config parameters have to be prefixed with `cd_`.

```txt
cd_k8s_versions="1.26.0,1.26.1,1.26.2,1.26.3,1.27.0"
cd_node_count_min="1"
cd_node_count_max="3"
cd_lifetime_limit="1h"
cd_session_timeout_limit="30m"
...
```

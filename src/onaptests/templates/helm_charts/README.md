# Local helm chart directory

It is adviced that a remote repository is used for simulators, to reduce local
complexity and avoid mistakes related to the duplicate code, submodules etc.

Place a .yaml file in this folder and mention it during HelmChartStep
initialization.

How a chart info .yaml file would look like:

```yaml
api_version: "v1"
app_version: "3.11.9"
chart_name: "mychart"
version: "0.1.0"
dependencies:
- name: "cassandra"
  version: "0.1.4"
  repository: "https://charts.kube-ops.io"
  local_repo_name: "kube-ops"
  values: {}
- name: "generate"
  repository: https://charts.kube-ops.io
  version: "~0.2.3"
  local_repo_name: "kube-ops"
  values: {}
```

All fields in the sample .yaml file above are required by the avionix library.
For more details, refer to the
[documentation](https://avionix.readthedocs.io/en/latest/reference/index.html).

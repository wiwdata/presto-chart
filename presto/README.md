# Presto Chart

[Presto](http://prestodb.io/) is an open source distributed SQL query engine 
originally created by Facebook that is used for running interactive analytic 
queries against data sources of all sizes.

## Chart Details

This chart will do the following:

* Install a deployment with a single coordinator.
* Install a configmap to manage the settings of the coordinator.
* Install a deployment with N number of workers for distributed processing.
* Install a configmap to manage the settings of the workers.
* Install a configmap containing the catalog of connectors from which presto
  will query.
* Install a service that exposes the http UI and API of the coordinator as
  desired.

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
$ helm install --name my-release --namespace my-namespace ./presto
```

## Configuration

Configurable values are documented in the `values.yaml`.

Specify each parameter using the `--set key=value[,key=value]` argument to 
`helm install`.

Alternatively, a YAML file that specifies the values for the parameters can 
be provided while installing the chart. For example,

```bash
$ helm install --name my-release -f values.yaml ./presto
```

> **Tip**: You can use the default [values.yaml](values.yaml)

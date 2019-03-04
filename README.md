# Presto Helm Chart

Highly configurable Helm Presto Chart based on the `stable/presto` chart
but significantly altered for greater flexibility:

- Specify connectors within the values.yaml file to easily manage them
  without modifying the image.
- Separated resources and selectors/affinities for coordinator and
  worker deployments given the different naturesmofmthe two
  deployments.
- Override and add configuration properties and JVM configuration
  within the values.yaml file.
- Templated bootstrapping within the containers allows for
  additional runtime configuration makes for more natural
  injection of environmental data. Particularly useful for
  rendering secrets into configurations and connectors via
  container environment variables.

# Chart Installation

This chart is packaged for easy install and any of the packaged versions stored
in the [charts](charts) directory can be installed via their download URL:

```bash
$ helm install \
  --name my-presto
  --namespace my-presto-namespace
  --values values.yaml
  https://github.com/wiwdata/presto-chart/raw/master/charts/presto-1.tgz
```

where the `values.yaml` is one you've created locally. For more details about
the chart see the chart [README](presto/README.md).

# Presto Helm Chart

Highly configurable Helm Presto Chart based on the `stable/presto` chart
but significantly altered for great flexibility.

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

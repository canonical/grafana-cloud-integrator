<!--
Avoid using this README file for information that is maintained or published elsewhere, e.g.:

* metadata.yaml > published on Charmhub
* documentation > published on (or linked to from) Charmhub
* detailed contribution guide > documentation or CONTRIBUTING.md

Use links instead.
-->

# Grafana Cloud Charmed Integrator for Kubernetes 

[![CharmHub Badge](https://charmhub.io/grafana-cloud-integrator/badge.svg)](https://charmhub.io/grafana-cloud-integrator)
[![Release](https://github.com/canonical/grafana-cloud-integrator/actions/workflows/release.yaml/badge.svg)](https://github.com/canonical/grafana-cloud-integrator/actions/workflows/release.yaml)
[![Discourse Status](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.charmhub.io&style=flat&label=CharmHub%20Discourse)](https://discourse.charmhub.io)

## Description

Charm for configuring Grafana Agent to ship telemetry to Grafana Cloud.

This charm allows the administrator to configure upstream endpoints, as well
as credentials, for shipping telemetry from a Juju deployed Grafana Agent
to Grafana Cloud.


This charm is useful when running the stack on-premise isn't desired, or
when an additional off-premise storage is used for redundancy.

This charm is useful for juju administrators who want to leverage the
observability relations provided by COS for use with Grafana Cloud.


## Getting Started

### Deploy the Integrator

Create a Juju model for your operator, say "observability"

```sh
juju add-model observability
```

The Grafana Cloud Charmed Integrator may now be deployed using the Juju command line as in

```sh
juju deploy grafana-cloud-integrator --channel=stable
```

### get a Grafana cloud token with the appropriate permissions

Get an API token with the following scopes to cover all the signals write permissions, you can change these to fit your needs and signals you intend to support with the deployment:

- metrics:write
- metrics:import
- logs:write
- traces:write
- alerts:write
- rules:write
- profiles:write

### Configuration Modes

The charm supports two credential modes:

- Shared credentials with `username` and `password`
- Per-signal credentials with `signal-credentials`

Do not set both modes at the same time. If both shared credentials and
`signal-credentials` are configured, the charm will go to `blocked`.

### Supported Signal Names

The `signal-credentials` option accepts a YAML mapping with these supported
top-level signal names:

- `prometheus`
- `loki`
- `tempo`
- `otlp`
- `pyroscope`

Each signal entry may define:

- `username`
- `password`

### Complete Example

This example configures:

- Prometheus remote write to Grafana Cloud
- Loki push to Grafana Cloud
- Tempo write to Grafana Cloud
- OTLP ingest to Grafana Cloud
- Pyroscope profile write to Grafana Cloud
- Separate credentials per signal

Create a `signals.yaml` file:

```yaml
prometheus:
  username: "1076854"
  password: "<api-token>"
loki:
  username: "639149"
  password: "glc_loki_token"
tempo:
  username: "123456"
  password: "glc_tempo_token"
otlp:
  instance-id: "1076854"
  password: "glc_otlp_token"
pyroscope:
  username: "424242"
  password: "glc_pyroscope_token"
```

If you also need to provide a custom CA, create `grafana-cloud-ca.pem`:

```pem
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
```

Then configure the charm:

```sh
juju deploy grafana-cloud-integrator --channel=stable

juju config grafana-cloud-integrator \
  prometheus-url="https://prometheus-prod-39-prod-eu-north-0.grafana.net/api/prom/push"

juju config grafana-cloud-integrator \
  loki-url="https://logs-prod-025.grafana.net/loki/api/v1/push"

juju config grafana-cloud-integrator \
  tempo-url="https://tempo-prod-10-prod-eu-north-0.grafana.net/otlp"

juju config grafana-cloud-integrator \
  otlp-url="https://otlp-gateway-prod-eu-north-0.grafana.net/otlp"

juju config grafana-cloud-integrator \
  pyroscope-url="https://profiles-prod-010.grafana.net"

juju config grafana-cloud-integrator \
  signal-credentials="$(cat signals.yaml)"

juju config grafana-cloud-integrator \
  tls-ca="$(cat grafana-cloud-ca.pem)"
```

Relate a consumer charm that supports the `grafana-cloud-config` interface:

```sh
juju relate alloy-sub grafana-cloud-integrator
```

Or:

```sh
juju relate alloy-vm grafana-cloud-integrator
```

Check status:

```sh
juju status grafana-cloud-integrator
juju status alloy-sub
```

### Copy-Paste Ready Example

This example creates the credentials file and configures the integrator in one
go.

```sh
cat > signals.yaml <<'EOF'
prometheus:
  username: "1076854"
  password: "glc_prometheus_token"
loki:
  username: "639149"
  password: "glc_loki_token"
tempo:
  username: "123456"
  password: "glc_tempo_token"
otlp:
  instance-id: "1076854"
  password: "glc_otlp_token"
pyroscope:
  username: "424242"
  password: "glc_pyroscope_token"
EOF

juju deploy grafana-cloud-integrator --channel=stable

juju config grafana-cloud-integrator \
  prometheus-url="https://prometheus-prod-39-prod-eu-north-0.grafana.net/api/prom/push" \
  loki-url="https://logs-prod-025.grafana.net/loki/api/v1/push" \
  tempo-url="https://tempo-prod-10-prod-eu-north-0.grafana.net/otlp" \
  otlp-url="https://otlp-gateway-prod-eu-north-0.grafana.net/otlp" \
  pyroscope-url="https://profiles-prod-010.grafana.net" \
  signal-credentials="$(cat signals.yaml)"

juju relate alloy-sub grafana-cloud-integrator
```

### Shared Credential Fallback

If the same Grafana Cloud credentials work for every configured signal, you
can use the legacy shared credential options instead:

```sh
juju config grafana-cloud-integrator \
  username="1076854" \
  password="glc_shared_token"
```

When shared credentials are used, the same username and password are exposed to
all configured signals.

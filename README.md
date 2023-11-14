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

### Basic Deployment

Create a Juju model for your operator, say "observability"

```sh
juju add-model observability
```

The Grafana Cloud Charmed Integrator may now be deployed using the Juju command line as in

```sh
juju deploy grafana-cloud-integrator --channel=stable
```


#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Grafana Cloud Integrator Charm."""

import typing

from charms.grafana_cloud_integrator.v0.cloud_config_provider import (
    Credentials,
    GrafanaCloudConfigProvider,
)
from ops import ActiveStatus, BlockedStatus, CharmBase, CollectStatusEvent


class GrafanaCloudIntegratorCharm(CharmBase):
    """Integrates local Grafana Agent deployments with Grafana Cloud."""

    def __init__(self, *args):
        super().__init__(*args)

        self._config = GrafanaCloudConfigProvider(
            self,
            Credentials(
                typing.cast(str, self.config.get("username", "")),
                typing.cast(str, self.config.get("password", "")),
            ),
            loki_url=typing.cast(str, self.config.get("loki-url", "")),
            tempo_url=typing.cast(str, self.config.get("tempo-url", "")),
            prometheus_url=typing.cast(str, self.config.get("prometheus-url", "")),
        )

        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

    def _on_collect_unit_status(self, event: CollectStatusEvent):
        # each *-url config option tells us where to send telemetry of a given type.
        # this maps config option names to human-readable telemetry types, so we can report
        # via the status which ones are unset. We strip the config value just in case.
        config_to_signal = (("loki-url", "Logs"), ("tempo-url", "Traces"), ("prometheus-url", "Metrics"))
        output_configs = {
            telemetry: bool(typing.cast(str, self.config.get(key, "")).strip()) for
            key, telemetry in config_to_signal
        }

        if not (self.config.get("username", "") and self.config.get("password", "")):
            # FIXME: should this be blocked in fact?
            event.add_status(ActiveStatus("username/password not configured."))

        if not any(output_configs.values()):
            event.add_status(BlockedStatus("No outputs configured"))
        elif any_unset := (k for k, v in output_configs.items() if not v):
            event.add_status(ActiveStatus(f"{', '.join(any_unset)} disabled"))
        else:
            event.add_status(ActiveStatus(""))


if __name__ == "__main__":  # pragma: nocover
    from ops import main

    main(GrafanaCloudIntegratorCharm)

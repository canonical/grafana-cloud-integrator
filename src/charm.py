#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Grafana Cloud Integrator Charm."""

from charms.grafana_cloud_integrator.v0.cloud_config_provider import (
    Credentials,
    GrafanaCloudConfigProvider,
)
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus


class GrafanaCloudIntegratorCharm(CharmBase):
    """Integrates local Grafana Agent deployments with Grafana Cloud."""

    def __init__(self, *args):
        super().__init__(*args)

        self._config = GrafanaCloudConfigProvider(
            self,
            Credentials(
                self.model.config.get("username", ""),
                self.model.config.get("password", ""),
            ),
            loki_url=self.model.config.get("loki-url", ""),
            prometheus_url=self.model.config.get("prometheus-url", ""),
        )

        for event in [
            self.on.config_changed,
            self.on.upgrade_charm,
            self.on.update_status,
        ]:
            self.framework.observe(event, self._on_config_changed)

    def _on_config_changed(self, event):
        self.unit.status = self.app.status = self._get_status()

    def _get_status(self):
        if not self.credentials_configured:
            return BlockedStatus("Credentials missing")

        if not self.loki_configured and not self.prom_configured:
            return BlockedStatus("No outputs configured")

        if not self.prom_configured:
            return ActiveStatus("Metrics disabled")

        if not self.loki_configured:
            return ActiveStatus("Logs disabled")

        return ActiveStatus("")

    def _is_not_empty(self, s):
        return bool(s and not s.isspace())

    @property
    def credentials_configured(self):
        """Whether the administrator has configured a username and password."""
        fields = (
            self.model.config.get("username", ""),
            self.model.config.get("password", ""),
        )

        return all(self._is_not_empty(x) for x in fields)

    @property
    def loki_configured(self):
        """Checks whether the Loki URL has been configured."""
        return self._is_not_empty(self.model.config.get("loki-url", ""))

    @property
    def prom_configured(self):
        """Checks whether the Prometheus URL has been configured."""
        return self._is_not_empty(self.model.config.get("prometheus-url", ""))


if __name__ == "__main__":  # pragma: nocover
    main(GrafanaCloudIntegratorCharm)

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
    SignalCredentials,
)
from ops import ActiveStatus, BlockedStatus, CharmBase, CollectStatusEvent

from signal_credentials import parse_signal_credentials


class GrafanaCloudIntegratorCharm(CharmBase):
    """Integrates local Grafana Agent deployments with Grafana Cloud."""

    def __init__(self, *args):
        super().__init__(*args)

        self._config = GrafanaCloudConfigProvider(
            self,
            self._shared_credentials,
            loki_url=typing.cast(str, self.config.get("loki-url", "")),
            tempo_url=typing.cast(str, self.config.get("tempo-url", "")),
            otlp_url=typing.cast(str, self.config.get("otlp-url", "")),
            pyroscope_url=typing.cast(str, self.config.get("pyroscope-url", "")),
            prometheus_url=typing.cast(str, self.config.get("prometheus-url", "")),
            signal_credentials=self._signal_credentials,
        )

        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

    @property
    def _shared_credentials(self) -> typing.Optional[Credentials]:
        """Return the shared credential pair when both values are configured."""
        username = typing.cast(str, self.config.get("username", "")).strip()
        password = typing.cast(str, self.config.get("password", "")).strip()
        if username and password:
            return Credentials(username, password)
        return None

    @property
    def _shared_credentials_configured(self) -> bool:
        """Check whether either shared credential config key is set."""
        username = typing.cast(str, self.config.get("username", "")).strip()
        password = typing.cast(str, self.config.get("password", "")).strip()
        return bool(username or password)

    @property
    def _signal_credentials_raw(self) -> str:
        """Return the raw structured signal credential config string."""
        return typing.cast(str, self.config.get("signal-credentials", ""))

    @property
    def _signal_credentials(self) -> SignalCredentials:
        """Parse the structured per-signal credentials from charm config."""
        return parse_signal_credentials(self._signal_credentials_raw)

    def _on_collect_unit_status(self, event: CollectStatusEvent):
        """Report readiness based on configured outputs and credential mode."""
        # each *-url config option tells us where to send telemetry of a given type.
        # this maps config option names to human-readable telemetry types, so we can report
        # via the status which ones are unset. We strip the config value just in case.
        if self._shared_credentials_configured and self._signal_credentials_raw.strip():
            event.add_status(
                BlockedStatus("Do not set both shared username/password and signal-credentials")
            )
            return

        try:
            self._signal_credentials
        except ValueError as exc:
            event.add_status(BlockedStatus(str(exc)))
            return

        config_to_signal = (
            ("loki-url", "Logs"),
            ("tempo-url", "Traces"),
            ("otlp-url", "OTLP"),
            ("pyroscope-url", "Profiles"),
            ("prometheus-url", "Metrics"),
        )
        output_configs = {
            telemetry: bool(typing.cast(str, self.config.get(key, "")).strip())
            for key, telemetry in config_to_signal
        }

        if not self._shared_credentials and not self._signal_credentials_raw.strip():
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

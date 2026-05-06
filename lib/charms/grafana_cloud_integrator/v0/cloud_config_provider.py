"""Grafana Cloud Integrator Configuration Requirer."""

from typing import MutableMapping, Optional

from ops.framework import Object

LIBID = "2a48eccc49a346f08879b11ecab4465a"
LIBAPI = 0
LIBPATCH = 8

DEFAULT_RELATION_NAME = "grafana-cloud-config"


class Credentials:
    """Credentials for the remote endpoints."""

    def __init__(self, username, password):
        self.username = username
        self.password = password


class SignalCredentials:
    """Credentials grouped by telemetry signal."""

    def __init__(
        self,
        prometheus: Optional[Credentials] = None,
        loki: Optional[Credentials] = None,
        tempo: Optional[Credentials] = None,
        otlp: Optional[Credentials] = None,
        pyroscope: Optional[Credentials] = None,
    ):
        self.prometheus = prometheus
        self.loki = loki
        self.tempo = tempo
        self.otlp = otlp
        self.pyroscope = pyroscope


class GrafanaCloudConfigProvider(Object):
    """Provider side of the Grafana Cloud Config relation."""

    def __init__(
        self,
        charm,
        credentials: Optional[Credentials],
        prometheus_url: str,
        loki_url: str,
        tempo_url: str,
        otlp_url: str,
        pyroscope_url: str,
        signal_credentials: Optional[SignalCredentials] = None,
        relation_name: str = DEFAULT_RELATION_NAME,
    ):
        super().__init__(charm, relation_name)
        self._charm = charm
        self._credentials = credentials
        self._prometheus_url = prometheus_url
        self._loki_url = loki_url
        self._tempo_url = tempo_url
        self._otlp_url = otlp_url
        self._pyroscope_url = pyroscope_url
        self._signal_credentials = signal_credentials or SignalCredentials()
        self._relation_name = relation_name

        relation_events = self._charm.on[relation_name]

        for event in [
            relation_events.relation_joined,
            relation_events.relation_created,
            relation_events.relation_changed,
            self._charm.on.config_changed,
        ]:
            self.framework.observe(
                event,
                self._on_relation_changed,
            )

    def _on_relation_changed(self, event):
        """Publish the currently configured Grafana Cloud settings to each relation."""
        if not self._charm.unit.is_leader():
            return

        for relation in self._charm.model.relations[self._relation_name]:
            databag = relation.data[self._charm.app]
            self._set_or_delete(databag, "username", self._credential_value("shared", "username"))
            self._set_or_delete(databag, "password", self._credential_value("shared", "password"))
            self._set_or_delete(databag, "prometheus_url", self._prometheus_url)
            self._set_or_delete(databag, "loki_url", self._loki_url)
            self._set_or_delete(databag, "tempo_url", self._tempo_url)
            self._set_or_delete(databag, "otlp_url", self._otlp_url)
            self._set_or_delete(databag, "pyroscope_url", self._pyroscope_url)
            self._set_or_delete(
                databag, "prometheus_username", self._credential_value("prometheus", "username")
            )
            self._set_or_delete(
                databag, "prometheus_password", self._credential_value("prometheus", "password")
            )
            self._set_or_delete(databag, "loki_username", self._credential_value("loki", "username"))
            self._set_or_delete(databag, "loki_password", self._credential_value("loki", "password"))
            self._set_or_delete(databag, "tempo_username", self._credential_value("tempo", "username"))
            self._set_or_delete(databag, "tempo_password", self._credential_value("tempo", "password"))
            self._set_or_delete(databag, "otlp_username", self._credential_value("otlp", "username"))
            self._set_or_delete(databag, "otlp_password", self._credential_value("otlp", "password"))
            self._set_or_delete(
                databag, "pyroscope_username", self._credential_value("pyroscope", "username")
            )
            self._set_or_delete(
                databag, "pyroscope_password", self._credential_value("pyroscope", "password")
            )
            self._set_or_delete(databag, "tls-ca", self._charm.config.get("tls-ca", ""))

    def _credential_value(self, signal: str, field: str) -> str:
        """Return a credential field for either the shared or signal-specific mode."""
        credentials = self._credentials if signal == "shared" else getattr(self._signal_credentials, signal)
        if not credentials:
            return ""
        return getattr(credentials, field)

    def _set_or_delete(self, databag: MutableMapping[str, str], key: str, value: Optional[str]) -> None:
        """Keep relation data in sync by removing empty values."""
        if value:
            databag[key] = value
            return
        databag.pop(key, None)

"""Grafana Cloud Integrator Configuration Requirer."""

from ops.framework import Object

LIBID = "2a48eccc49a346f08879b11ecab4465a"
LIBAPI = 0
LIBPATCH = 4

DEFAULT_RELATION_NAME = "grafana-cloud-config"

class Credentials:
    """Credentials for the remote endpoints."""
    def __init__(self, username, password):
        self.username = username
        self.password = password

class GrafanaCloudConfigProvider(Object):
    """Provider side of the Grafana Cloud Config relation."""

    def __init__(
        self,
        charm,
        credentials: Credentials,
        prometheus_url: str,
        loki_url: str,
        relation_name: str = DEFAULT_RELATION_NAME,
    ):
        super().__init__(charm, relation_name)
        self._charm = charm
        self._credentials = credentials
        self._prometheus_url = prometheus_url
        self._loki_url = loki_url
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
        if not self._charm.unit.is_leader():
            return

        for relation in self._charm.model.relations[self._relation_name]:
            databag = relation.data[self._charm.app]
            if self._credentials:
                databag["username"] = self._credentials.username
                databag["password"] = self._credentials.password
            if self._charm.loki_configured:
                databag["loki_url"] = self._loki_url
            if self._charm.prom_configured:
                databag["prometheus_url"] = self._prometheus_url
            databag["tls-ca"] = self._charm.config.get("tls-ca", "")

from unittest.mock import patch

import pytest
from charms.grafana_cloud_integrator.v0.cloud_config_requirer import (
    CloudConfigAvailableEvent,
    CloudConfigRevokedEvent,
    GrafanaCloudConfigRequirer,
)
from ops import CharmBase, Framework
from ops.testing import Harness
from scenario import Context, Relation, State


class MyCharm(CharmBase):
    def __init__(self, framework: Framework):
        super().__init__(framework)
        self.cloud = GrafanaCloudConfigRequirer(self)


@pytest.fixture()
def mycharm_context():
    """Returns a Context object with a MyCharm instance."""
    return Context(
        charm_type=MyCharm,
        meta={
            "name": "my-charm",
            "requires": {
                "grafana-cloud-config": {"interface": "grafana_cloud_config", "limit": 1}
            },
        },
    )


@pytest.mark.parametrize("is_leader", [(True,), (False,)])
def test_requirer_emits_cloud_config_available_event_on_relation_changed(
    is_leader, mycharm_context
):
    # GIVEN a grafana-cloud-config relation and a leadership status
    grafana_cloud_config_relation = Relation("grafana-cloud-config")
    state = State(leader=is_leader, relations=[grafana_cloud_config_relation])

    # WHEN the grafana-cloud-config relation changes
    mycharm_context.run(
        mycharm_context.on.relation_changed(relation=grafana_cloud_config_relation), state
    )

    # THEN the CloudConfigAvailableEvent event is emitted
    assert any(
        event
        for event in mycharm_context.emitted_events
        if isinstance(event, CloudConfigAvailableEvent)
    )


@pytest.mark.parametrize("is_leader", [(True,), (False,)])
def test_requirer_emits_cloud_config_revoked_event_on_relation_broken(is_leader, mycharm_context):
    # GIVEN a grafana-cloud-config relation
    grafana_cloud_config_relation = Relation("grafana-cloud-config")
    # AND GIVEN leadership/non-leadership
    state = State(leader=is_leader, relations=[grafana_cloud_config_relation])

    # WHEN the grafana-cloud-config relation changes
    mycharm_context.run(
        mycharm_context.on.relation_broken(relation=grafana_cloud_config_relation), state
    )

    # THEN the CloudConfigAvailableEvent event is emitted
    assert any(
        event
        for event in mycharm_context.emitted_events
        if isinstance(event, CloudConfigRevokedEvent)
    )


def test_requirer_reads_signal_specific_credentials(mycharm_context):
    harness = Harness(
        MyCharm,
        meta="""
name: my-charm
requires:
  grafana-cloud-config:
    interface: grafana_cloud_config
""",
    )
    harness.begin()
    relation_id = harness.add_relation("grafana-cloud-config", "grafana-cloud-integrator")
    harness.add_relation_unit(relation_id, "grafana-cloud-integrator/0")
    harness.update_relation_data(
        relation_id,
        "grafana-cloud-integrator",
        {
            "prometheus_url": "https://prom.example/api/prom/push",
            "prometheus_username": "1076854",
            "prometheus_password": "prom-token",
            "loki_url": "https://logs.example/loki/api/v1/push",
            "loki_username": "639149",
            "loki_password": "loki-token",
            "otlp_url": "https://otlp.example/otlp",
            "otlp_username": "otlp-instance",
            "otlp_password": "otlp-token",
            "pyroscope_url": "https://profiles.example",
            "pyroscope_username": "profile-user",
            "pyroscope_password": "profile-token",
        },
    )

    cloud = harness.charm.cloud
    assert cloud.prometheus_url == "https://prom.example/api/prom/push"
    prometheus_credentials = cloud.prometheus_credentials
    assert prometheus_credentials is not None
    assert prometheus_credentials.username == "1076854"
    assert prometheus_credentials.password == "prom-token"
    assert cloud.loki_url == "https://logs.example/loki/api/v1/push"
    loki_credentials = cloud.loki_credentials
    assert loki_credentials is not None
    assert loki_credentials.username == "639149"
    assert loki_credentials.password == "loki-token"
    assert cloud.otlp_url == "https://otlp.example/otlp"
    otlp_credentials = cloud.otlp_credentials
    assert otlp_credentials is not None
    assert otlp_credentials.username == "otlp-instance"
    assert otlp_credentials.password == "otlp-token"
    assert cloud.pyroscope_url == "https://profiles.example"
    pyroscope_credentials = cloud.pyroscope_credentials
    assert pyroscope_credentials is not None
    assert pyroscope_credentials.username == "profile-user"
    assert pyroscope_credentials.password == "profile-token"


def test_requirer_falls_back_to_shared_credentials(mycharm_context):
    harness = Harness(
        MyCharm,
        meta="""
name: my-charm
requires:
  grafana-cloud-config:
    interface: grafana_cloud_config
""",
    )
    harness.begin()
    relation_id = harness.add_relation("grafana-cloud-config", "grafana-cloud-integrator")
    harness.add_relation_unit(relation_id, "grafana-cloud-integrator/0")
    harness.update_relation_data(
        relation_id,
        "grafana-cloud-integrator",
        {
            "prometheus_url": "https://prom.example/api/prom/push",
            "loki_url": "https://logs.example/loki/api/v1/push",
            "otlp_url": "https://otlp.example/otlp",
            "pyroscope_url": "https://profiles.example",
            "username": "shared-user",
            "password": "shared-pass",
        },
    )

    cloud = harness.charm.cloud
    prometheus_credentials = cloud.prometheus_credentials
    assert prometheus_credentials is not None
    assert prometheus_credentials.username == "shared-user"
    assert prometheus_credentials.password == "shared-pass"
    loki_credentials = cloud.loki_credentials
    assert loki_credentials is not None
    assert loki_credentials.username == "shared-user"
    assert loki_credentials.password == "shared-pass"
    otlp_credentials = cloud.otlp_credentials
    assert otlp_credentials is not None
    assert otlp_credentials.username == "shared-user"
    assert otlp_credentials.password == "shared-pass"
    pyroscope_credentials = cloud.pyroscope_credentials
    assert pyroscope_credentials is not None
    assert pyroscope_credentials.username == "shared-user"
    assert pyroscope_credentials.password == "shared-pass"


def test_requirer_does_not_log_relation_databag_contents():
    harness = Harness(
        MyCharm,
        meta="""
name: my-charm
requires:
  grafana-cloud-config:
    interface: grafana_cloud_config
""",
    )
    harness.begin()
    relation_id = harness.add_relation("grafana-cloud-config", "grafana-cloud-integrator")
    harness.add_relation_unit(relation_id, "grafana-cloud-integrator/0")
    harness.update_relation_data(
        relation_id,
        "grafana-cloud-integrator",
        {
            "username": "sensitive-user",
            "password": "sensitive-pass",
        },
    )

    with patch("charms.grafana_cloud_integrator.v0.cloud_config_requirer.logger.info") as info_log:
        assert harness.charm.cloud.credentials is not None

    info_log.assert_not_called()

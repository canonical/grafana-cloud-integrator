import pytest
from charms.grafana_cloud_integrator.v0.cloud_config_requirer import (
    CloudConfigAvailableEvent,
    CloudConfigRevokedEvent,
    GrafanaCloudConfigRequirer,
)
from ops import CharmBase, Framework
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


@pytest.mark.parametrize(
    "is_leader",
    [
        (True,),
        (False,),
    ],
)
def test_requirer_emits_cloud_config_available_event_on_relation_changed(is_leader, mycharm_context):
    # GIVEN a grafana-cloud-config relation and a leadership status
    grafana_cloud_config_relation = Relation("grafana-cloud-config")
    state = State(leader=is_leader, relations=[grafana_cloud_config_relation])

    # WHEN the grafana-cloud-config relation changes
    mycharm_context.run(grafana_cloud_config_relation.changed_event, state)

    # THEN the CloudConfigAvailableEvent event is emitted
    assert any(event for event in mycharm_context.emitted_events if isinstance(event, CloudConfigAvailableEvent))


@pytest.mark.parametrize(
    "is_leader",
    [
        (True,),
        (False,),
    ],
)
def test_requirer_emits_cloud_config_revoked_event_on_relation_broken(is_leader, mycharm_context):
    # GIVEN a grafana-cloud-config relation
    grafana_cloud_config_relation = Relation("grafana-cloud-config")
    # AND GIVEN leadership/non-leadership
    state = State(leader=is_leader, relations=[grafana_cloud_config_relation])

    # WHEN the grafana-cloud-config relation changes
    mycharm_context.run(grafana_cloud_config_relation.broken_event, state)

    # THEN the CloudConfigAvailableEvent event is emitted
    assert any(event for event in mycharm_context.emitted_events if isinstance(event, CloudConfigRevokedEvent))

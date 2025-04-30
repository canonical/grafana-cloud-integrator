# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest

import ops.testing
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness

from charm import GrafanaCloudIntegratorCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
        self.addCleanup(setattr, ops.testing, "SIMULATE_CAN_CONNECT", False)

        self.harness = Harness(GrafanaCloudIntegratorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.harness.set_leader(True)

    def test_no_urls_set(self):
        """Test that when no URL has been set, the charm knows about it."""
        # Given Prometheus and Loki URLs
        # When not configured
        # Then it should toggle configuration status of both to false

        self.harness.update_config()
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, BlockedStatus)

    def test_prometheus_url_is_propagated(self):
        """Test that when a Prometheus URL has been configured, the charm knows about it."""
        # Given a Prometheus URL
        # When configured
        # Then it should toggle prom configured to true

        self.harness.update_config({"prometheus-url": "https://example.org"})
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

    def test_loki_url_is_propagated(self):
        """Test that when a Loki URL has been configured, the charm knows about it."""
        # Given a Loki URL
        # When configured
        # Then it should toggle loki configured to true

        self.harness.update_config({"loki-url": "https://example.org"})
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

    def test_credentials_are_propagated_only_username(self):
        """Test that when only username has been configured, the charm knows about it."""
        # Given Credentials
        # When only username is configured
        # Then it should toggle credentials configured to false

        self.harness.update_config({"username": "a-username", "loki-url": "foo"})
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

    def test_credentials_are_propagated_only_password(self):
        """Test that when only password has been configured, the charm knows about it."""
        # Given Credentials
        # When only password  is configured
        # Then it should toggle credentials configured to false

        self.harness.update_config({"password": "a-password", "loki-url": "foo"})
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

    def test_credentials_are_propagated_both(self):
        """Test that when credentials have been configured, the charm knows about it."""
        # Given Credentials
        # When both username and password are configured
        # Then it should toggle credentials configured to true

        self.harness.update_config({"username": "a-username", "password": "a-password", "loki-url": "https://example.org"})
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

    def test_everything_is_configured(self):
        """Test that when everything is configured, the charm knows it."""
        # Given charm config
        # When all values are configured
        # Then the charm should be set to active

        self.harness.update_config(
            {
                "username": "a-username",
                "password": "a-password",
                "prometheus-url": "https://example.org",
                "loki-url": "https://example.org",
            }
        )
        self.harness.evaluate_status()
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest

import ops.testing
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
from ops.testing import Harness

from charm import GrafanaCloudIntegratorCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        ops.testing.SIMULATE_CAN_CONNECT = True
        self.addCleanup(setattr, ops.testing, "SIMULATE_CAN_CONNECT", False)

        self.harness = Harness(GrafanaCloudIntegratorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.harness.set_leader(True)

    def test_no_urls_set(self):
        """
            Given Prometheus and Loki URLs
            When not configured
            Then it should toggle configuration status of both to false 
        """
        self.harness.update_config()
        self.assertFalse(self.harness.charm.prom_configured)
        self.assertFalse(self.harness.charm.loki_configured)
        self.assertIsInstance(self.harness.model.unit.status, BlockedStatus)


    def test_prometheus_url_is_propagated(self):
        """
            Given a Prometheus URL
            When configured
            Then it should toggle prom configured to true 
        """

        self.harness.update_config({
            "prometheus-url": "https://example.org"
        })

        self.assertTrue(self.harness.charm.prom_configured)
        self.assertFalse(self.harness.charm.loki_configured)
        self.assertIsInstance(self.harness.model.unit.status, BlockedStatus)


    def test_loki_url_is_propagated(self):
        """
            Given a Loki URL
            When configured
            Then it should toggle loki configured to true 
        """

        self.harness.update_config({
            "loki-url": "https://example.org"
        })

        self.assertTrue(self.harness.charm.loki_configured)
        self.assertFalse(self.harness.charm.prom_configured)
        self.assertIsInstance(self.harness.model.unit.status, BlockedStatus)



    def test_credentials_are_propagated_only_username(self):
        """
            Given Credentials
            When only username is configured
            Then it should toggle credentials configured to false 
        """

        self.harness.update_config({
            "username": "a-username"
        })

        self.assertFalse(self.harness.charm.credentials_configured)
        self.assertIsInstance(self.harness.model.unit.status, BlockedStatus)

    def test_credentials_are_propagated_only_password(self):
        """
            Given Credentials
            When only password  is configured
            Then it should toggle credentials configured to false 
        """

        self.harness.update_config({
            "password": "a-password"
        })

        self.assertFalse(self.harness.charm.credentials_configured)
        self.assertIsInstance(self.harness.model.unit.status, BlockedStatus)

    def test_credentials_are_propagated_both(self):
        """
            Given Credentials
            When both username and password are configured
            Then it should toggle credentials configured to true 
        """

        self.harness.update_config({
            "username": "a-username",
            "password": "a-password"
        })

        self.assertTrue(self.harness.charm.credentials_configured)

    def test_everything_is_configured(self):
        """
            Given charm config
            When all values are configured
            Then the charm should be set to active 
        """

        self.harness.update_config({
            "username": "a-username",
            "password": "a-password",
            "prometheus-url": "https://example.org",
            "loki-url": "https://example.org"
        })

        self.assertTrue(self.harness.charm.credentials_configured)
        self.assertIsInstance(self.harness.model.unit.status, ActiveStatus)

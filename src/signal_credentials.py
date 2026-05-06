"""Helpers for parsing signal-specific Grafana Cloud credentials."""

from typing import Any, Mapping, Optional

import yaml
from charms.grafana_cloud_integrator.v0.cloud_config_provider import Credentials, SignalCredentials


def parse_signal_credentials(raw_value: str) -> SignalCredentials:
    """Parse YAML signal credentials into a typed per-signal credential set.

    The parser accepts a top-level mapping where each key is a telemetry signal
    name and each value is a mapping containing `username` and `password`.
    """
    if not raw_value.strip():
        return SignalCredentials()

    parsed = yaml.safe_load(raw_value)
    if parsed is None:
        return SignalCredentials()
    if not isinstance(parsed, Mapping):
        raise ValueError("signal-credentials must be a mapping")

    credentials_by_signal = {}
    for signal_name, signal_config in parsed.items():
        credentials = _parse_signal_entry(signal_name, signal_config)
        if credentials is not None:
            credentials_by_signal[str(signal_name)] = credentials

    return SignalCredentials(
        prometheus=credentials_by_signal.get("prometheus"),
        loki=credentials_by_signal.get("loki"),
        tempo=credentials_by_signal.get("tempo"),
        otlp=credentials_by_signal.get("otlp"),
        pyroscope=credentials_by_signal.get("pyroscope"),
    )


def _parse_signal_entry(signal_name: Any, signal_config: Any) -> Optional[Credentials]:
    """Parse one signal entry and validate that the pair is complete."""
    if signal_config is None:
        return None
    if not isinstance(signal_config, Mapping):
        raise ValueError(f"signal-credentials.{signal_name} must be a mapping")

    username = _coerce_string(
        signal_config.get("instance-id") if str(signal_name) == "otlp" else signal_config.get("username")
    ) or _coerce_string(signal_config.get("username"))
    password = _coerce_string(signal_config.get("password"))

    if bool(username) != bool(password):
        raise ValueError(
            f"signal-credentials.{signal_name} must define both "
            f"{'instance-id' if str(signal_name) == 'otlp' else 'username'} and password"
        )
    if not username:
        return None
    return Credentials(username=username, password=password)


def _coerce_string(value: Any) -> str:
    """Normalize config values to stripped strings."""
    if value is None:
        return ""
    return str(value).strip()

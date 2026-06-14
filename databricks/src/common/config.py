"""Configuration and secret loading — the single place env/secrets are read.

No other module hardcodes credentials or reads ``os.environ`` directly
(PRD Section 10 "Security: all secrets in Key Vault, none in code"; roadmap
Step 0.5). Locally values come from a git-ignored ``.env`` file; on Databricks
and Azure the same names are injected as real environment variables (sourced
from Key Vault), and this loader reads them transparently either way.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env once at import time if it exists. This is a no-op in CI or on
# Databricks, where real environment variables are injected instead of a file.
load_dotenv()


def get_required(name: str) -> str:
    """Return an environment variable or fail loudly.

    Secrets must never silently default to an empty value — a missing token
    should stop the pipeline at startup, not produce a confusing 401 later.
    """
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set")
    return value


def get_optional(name: str, default: str | None = None) -> str | None:
    """Return an environment variable, or ``default`` if it is unset/empty."""
    value = os.environ.get(name)
    return value if value else default


@dataclass(frozen=True)
class Settings:
    """Typed, immutable view over the environment.

    Add a field here as each phase introduces a new credential, so the whole
    project has one discoverable list of what configuration exists.
    """

    entsoe_api_token: str | None = None
    eventhub_connection_string: str | None = None
    eventhub_name: str | None = None
    redis_url: str | None = None
    neo4j_uri: str | None = None
    neo4j_user: str | None = None
    neo4j_password: str | None = None
    openlineage_url: str | None = None
    openlineage_namespace: str | None = None

    @classmethod
    def load(cls) -> Settings:
        """Build a Settings instance from the current environment."""
        return cls(
            entsoe_api_token=get_optional("ENTSOE_API_TOKEN"),
            eventhub_connection_string=get_optional("EVENTHUB_CONNECTION_STRING"),
            eventhub_name=get_optional("EVENTHUB_NAME"),
            redis_url=get_optional("REDIS_URL"),
            neo4j_uri=get_optional("NEO4J_URI"),
            neo4j_user=get_optional("NEO4J_USER"),
            neo4j_password=get_optional("NEO4J_PASSWORD"),
            openlineage_url=get_optional("OPENLINEAGE_URL"),
            openlineage_namespace=get_optional("OPENLINEAGE_NAMESPACE", "ev-battery-grid"),
        )

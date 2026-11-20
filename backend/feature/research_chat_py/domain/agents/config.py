"""Dynamic agent configuration via AWS AppConfig Lambda extension."""
from __future__ import annotations

import json
import os
import urllib.request

_DEFAULTS = {
    "model_id": "global.anthropic.claude-sonnet-4-6",
    "max_tokens": 4096,
    "temperature": 0.3,
}


def get_agent_config() -> dict:
    """Fetch config from AppConfig Lambda extension (localhost:2772).

    Falls back to defaults when running locally without the extension.
    """
    app = os.environ.get("APPCONFIG_APP")
    env = os.environ.get("APPCONFIG_ENV")
    profile = os.environ.get("APPCONFIG_PROFILE")

    if not all([app, env, profile]):
        return _DEFAULTS

    url = f"http://localhost:2772/applications/{app}/environments/{env}/configurations/{profile}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return _DEFAULTS

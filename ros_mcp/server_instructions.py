"""Server-level guidance exposed to every MCP client during initialization."""

from __future__ import annotations

import os
from pathlib import Path


DEFAULT_SERVER_INSTRUCTIONS = """Use the ROS tools as an observe-decide-act interface.
Read tool descriptions before calling a tool. If a verified robot specification is
available, load it and follow its operational guidance before controlling that robot.
Use read-only observations when they materially help the request, make bounded motion
commands, re-observe when executing a perception-dependent task, and explicitly stop
continuous velocity controllers when the requested motion is complete. Do not write to
a robot unless the user or MCP host has identified it as the active target."""


def load_server_instructions() -> str:
    """Load deployment guidance from a file or inline environment override."""
    instructions_file = os.getenv("ROS_MCP_INSTRUCTIONS_FILE", "").strip()
    if instructions_file:
        path = Path(instructions_file).expanduser()
        try:
            content = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read ROS_MCP_INSTRUCTIONS_FILE={path}: {exc}") from exc
        if not content:
            raise RuntimeError(f"ROS_MCP_INSTRUCTIONS_FILE is empty: {path}")
        return content

    inline = os.getenv("ROS_MCP_INSTRUCTIONS", "").strip()
    return inline or DEFAULT_SERVER_INSTRUCTIONS

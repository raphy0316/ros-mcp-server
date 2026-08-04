"""Server-level guidance exposed to every MCP client during initialization."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


DEFAULT_SERVER_INSTRUCTIONS = """Use the ROS tools as an observe-decide-act interface.
Read tool descriptions before calling a tool. If a verified robot specification is
available, load it and follow its operational guidance before controlling that robot.
Use read-only observations when they materially help the request, make bounded motion
commands, re-observe when executing a perception-dependent task, and explicitly stop
continuous velocity controllers when the requested motion is complete. Do not write to
a robot unless the user or MCP host has identified it as the active target."""


def _load_robot_spec_prompts(name: str) -> str:
    normalized = name.strip().replace(" ", "_")
    if not normalized or Path(normalized).name != normalized:
        raise RuntimeError(f"Invalid ROS_MCP_ROBOT_SPEC name: {name!r}")

    spec_path = Path(__file__).parent.parent / "robot_specifications" / f"{normalized}.yaml"
    try:
        config = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise RuntimeError(f"Unable to read ROS_MCP_ROBOT_SPEC={normalized}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Invalid robot specification YAML for {normalized}: {exc}") from exc

    prompts = config.get("prompts")
    if not isinstance(prompts, str) or not prompts.strip():
        raise RuntimeError(f"Robot specification has no prompts: {spec_path}")
    return prompts.strip()


def load_server_instructions() -> str:
    """Load deployment guidance and append an optional verified robot specification."""
    instructions_file = os.getenv("ROS_MCP_INSTRUCTIONS_FILE", "").strip()
    if instructions_file:
        path = Path(instructions_file).expanduser()
        try:
            content = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read ROS_MCP_INSTRUCTIONS_FILE={path}: {exc}") from exc
        if not content:
            raise RuntimeError(f"ROS_MCP_INSTRUCTIONS_FILE is empty: {path}")
        instructions = content
    else:
        inline = os.getenv("ROS_MCP_INSTRUCTIONS", "").strip()
        instructions = inline or DEFAULT_SERVER_INSTRUCTIONS

    robot_spec = os.getenv("ROS_MCP_ROBOT_SPEC", "").strip()
    if not robot_spec:
        return instructions

    spec_prompts = _load_robot_spec_prompts(robot_spec)
    return (
        f"{instructions}\n\n"
        f"VERIFIED ROBOT SPECIFICATION ({robot_spec})\n"
        f"{spec_prompts}"
    )

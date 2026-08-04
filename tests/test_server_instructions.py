from ros_mcp.server_instructions import DEFAULT_SERVER_INSTRUCTIONS, load_server_instructions
from ros_mcp.utils.config_utils import get_verified_robot_spec_util


def test_server_instructions_default(monkeypatch) -> None:
    monkeypatch.delenv("ROS_MCP_INSTRUCTIONS_FILE", raising=False)
    monkeypatch.delenv("ROS_MCP_INSTRUCTIONS", raising=False)
    monkeypatch.delenv("ROS_MCP_ROBOT_SPEC", raising=False)

    assert load_server_instructions() == DEFAULT_SERVER_INSTRUCTIONS


def test_server_instructions_file_takes_precedence(monkeypatch, tmp_path) -> None:
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text("deployment guidance\n", encoding="utf-8")
    monkeypatch.setenv("ROS_MCP_INSTRUCTIONS", "inline guidance")
    monkeypatch.setenv("ROS_MCP_INSTRUCTIONS_FILE", str(instructions_file))
    monkeypatch.delenv("ROS_MCP_ROBOT_SPEC", raising=False)

    assert load_server_instructions() == "deployment guidance"


def test_robot_spec_is_merged_into_initial_server_instructions(monkeypatch) -> None:
    monkeypatch.delenv("ROS_MCP_INSTRUCTIONS_FILE", raising=False)
    monkeypatch.setenv("ROS_MCP_INSTRUCTIONS", "deployment guidance")
    monkeypatch.setenv("ROS_MCP_ROBOT_SPEC", "contoro_isaac_sim")

    instructions = load_server_instructions()

    assert instructions.startswith("deployment guidance")
    assert "VERIFIED ROBOT SPECIFICATION (contoro_isaac_sim)" in instructions
    assert "/<robot_id>/camera/pov/image_raw" in instructions
    assert "/robot_1/world_odom" in instructions
    assert "do not default to timid" in instructions
    assert "one appropriately sized continuous" in instructions
    assert "rather than after every short command" in instructions
    assert "rate_hz: 10" in instructions
    assert "at least 0.35 m/s" in instructions
    assert "Prefer 1.5 m/s" in instructions
    assert "Prefer 1.8 m/s" in instructions
    assert "normally uses 1.7 m/s" in instructions
    assert "0.5 rad/s as the normal turning speed" in instructions
    assert "prefer 0.4 rad/s for normal turning" in instructions
    assert "Unitree H1" in instructions
    assert "robot_1: x=0.3, y=-3.0" in instructions
    assert "robot_2: x=0.0, y=3.0" in instructions
    assert "robot_3: x=0.0, y=9.0" in instructions
    assert "return to its original position" in instructions
    assert "without rebasing" in instructions


def test_contoro_verified_spec_exposes_operational_topics() -> None:
    spec = get_verified_robot_spec_util("contoro_isaac_sim")["contoro_isaac_sim"]

    assert "/<robot_id>/camera/pov/image_raw" in spec["prompts"]
    assert "/robot_1/world_odom" in spec["prompts"]
    assert "once after completion" in spec["prompts"]
    assert "without a scene, safety, or precision reason" in spec["prompts"]
    assert "unnecessarily short increments" in spec["prompts"]
    assert "rate_hz: 10" in spec["prompts"]
    assert "at least 0.35 m/s" in spec["prompts"]
    assert "Prefer 1.5 m/s" in spec["prompts"]
    assert "Prefer 1.8 m/s" in spec["prompts"]
    assert "normally uses 1.7 m/s" in spec["prompts"]
    assert "yellow-and-black" in spec["prompts"]
    assert "root z=0.8" in spec["prompts"]
    assert "home yaw=0.0" in spec["prompts"]

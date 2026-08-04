from ros_mcp.server_instructions import DEFAULT_SERVER_INSTRUCTIONS, load_server_instructions
from ros_mcp.utils.config_utils import get_verified_robot_spec_util


def test_server_instructions_default(monkeypatch) -> None:
    monkeypatch.delenv("ROS_MCP_INSTRUCTIONS_FILE", raising=False)
    monkeypatch.delenv("ROS_MCP_INSTRUCTIONS", raising=False)

    assert load_server_instructions() == DEFAULT_SERVER_INSTRUCTIONS


def test_server_instructions_file_takes_precedence(monkeypatch, tmp_path) -> None:
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text("deployment guidance\n", encoding="utf-8")
    monkeypatch.setenv("ROS_MCP_INSTRUCTIONS", "inline guidance")
    monkeypatch.setenv("ROS_MCP_INSTRUCTIONS_FILE", str(instructions_file))

    assert load_server_instructions() == "deployment guidance"


def test_contoro_verified_spec_exposes_operational_topics() -> None:
    spec = get_verified_robot_spec_util("contoro_isaac_sim")["contoro_isaac_sim"]

    assert "/<robot_id>/camera/pov/image_raw" in spec["prompts"]
    assert "/robot_1/world_odom" in spec["prompts"]
    assert "rate_hz: 10" in spec["prompts"]

import json
import os
from pathlib import Path

import pytest

from config.config_manager import ConfigManager


@pytest.mark.unit
def test_config_manager_path_is_independent_of_working_directory(
    monkeypatch,
    tmp_path,
):
    original_cwd = Path.cwd()

    monkeypatch.chdir(tmp_path)

    manager = ConfigManager()

    expected_path = (
        Path(__file__).resolve().parents[2]
        / "config"
        / "user.json"
    )

    assert manager.file == expected_path


@pytest.mark.unit
def test_config_manager_loads_and_saves_user_config():
    manager = ConfigManager()

    manager.set(
        "_test_config_manager_key",
        "test_value",
    )

    assert manager.get(
        "_test_config_manager_key"
    ) == "test_value"
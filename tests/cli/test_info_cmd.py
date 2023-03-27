"""Unit tests for the info CLI command."""
# tests/cli/test_info_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import docker 
from rich.console import Console
from rich.table import Table
import io
import tests.fake_data as fake_data
import json

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)
test_docker_client = docker.from_env()

## Test helpers

class mockImage:
    def __init__(self, tags: list[str]):
        self.tags = tags

def get_test_image_list() -> list[mockImage]:
    test_image_list = []
    test_image_list.append(mockImage(["alpine:latest"]))
    test_image_list.append(mockImage([""]))
    test_image_list.append(mockImage(["make_gnu_arm:v1.0.0"]))
    test_image_list.append(mockImage(["stlink_org:latest", "stlink_org:v1.0.0'"]))
    test_image_list.append(mockImage(["cpputest:latest"]))
    test_image_list.append(mockImage(["make_gnu_arm:latest"]))
    test_image_list.append(mockImage(["debian:latest"]))
    test_image_list.append(mockImage(["ubuntu:latest"]))
    test_image_list.append(mockImage(["hello-world:latest"]))
    test_image_list.append(mockImage([""]))
    return test_image_list

def get_expected_table(expected_tools: list[list[str]]) ->str:
    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_column("Status")
    for expected_tool in expected_tools:
        expected_table.add_row(*expected_tool)
    console = Console(file=io.StringIO())
    console.print(expected_table)
    return console.file.getvalue()

## Test cases

@patch("dem.cli.command.info_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.info_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.info_cmd.registry.list_repos")
def test_info_arg_demo(mock_list_repos, mock_ContainerEngine, mock_read_deserialized_dev_env_json):
    # Test setup
    test_local_images = [
        "axemsolutions/make_gnu_arm:v1.0.0",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/stlink_org:v1.0.0",
        "axemsolutions/cpputest:latest",
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/make_gnu_arm:v0.1.0", 
        "axemsolutions/make_gnu_arm:v1.1.0",
    ]
    test_registry_images = [
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest", 
    ]
    mock_read_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_tool_images.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", "demo"], color=True)

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_tools = [
        ["build system", "axemsolutions/make_gnu_arm:latest", "Image is available locally and in the registry."],
        ["toolchain", "axemsolutions/make_gnu_arm:latest", "Image is available locally and in the registry."],
        ["debugger", "axemsolutions/stlink_org:latest", "Image is available locally and in the registry."],
        ["deployer", "axemsolutions/stlink_org:latest", "Image is available locally and in the registry."],
        ["test framework", "axemsolutions/cpputest:latest", "Image is available locally and in the registry."],
    ]
    assert get_expected_table(expected_tools)  == runner_result.stdout


@patch("dem.cli.command.info_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.info_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.info_cmd.registry.list_repos")
def test_info_arg_nagy_cica_project(mock_list_repos, mock_ContainerEngine, 
                                    mock_read_deserialized_dev_env_json):
    # Test setup
    test_local_images = [
        "axemsolutions/make_gnu_arm:v1.0.0",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/stlink_org:v1.0.0",
        "axemsolutions/cpputest:latest",
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/make_gnu_arm:v0.1.0", 
        "axemsolutions/make_gnu_arm:v1.1.0",
        "axemsolutions/jlink:latest",
    ]
    test_registry_images = [
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest", 
    ]
    mock_read_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_tool_images.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", "nagy_cica_project"], color=True)

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_tools = [
        ["build system", "axemsolutions/bazel:latest", "[red]Error: Image is not available.[/]"],
        ["toolchain", "axemsolutions/gnu_arm:latest", "[red]Error: Image is not available.[/]"],
        ["debugger", "axemsolutions/jlink:latest", "Image is available locally."],
        ["deployer", "axemsolutions/jlink:latest", "Image is available locally."],
        ["test framework", "axemsolutions/cpputest:latest", "Image is available locally and in the registry."],
    ]
    assert get_expected_table(expected_tools) == runner_result.stdout

@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_info_arg_invalid(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_local_json, 
                          mock_DevEnvOrgSetup, mock_read_deserialized_dev_env_org_json):
    # Test setup
    fake_deserialized_dev_env_json = MagicMock()
    mock_read_deserialized_dev_env_local_json.return_value = fake_deserialized_dev_env_json
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup

    fake_deserialized_dev_env_org_json = MagicMock()
    mock_read_deserialized_dev_env_org_json.return_value = fake_deserialized_dev_env_org_json
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", "not_existing_environment"])

    # Check expectations
    mock_read_deserialized_dev_env_local_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_dev_env_json)

    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_DevEnvOrgSetup.assert_called_once_with(fake_deserialized_dev_env_org_json)
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: Unknown Development Environment: not_existing_environment[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr

@patch("dem.cli.command.info_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.info_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.info_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.info_cmd.registry.list_repos")
def test_info_org_dev_env(mock_list_repos, mock_ContainerEngine, 
                                    mock_read_deserialized_dev_env_json,
                                    mock_read_deserialized_dev_env_org_json):
    # Test setup
    test_local_images = [
        "axemsolutions/make_gnu_arm:v1.0.0",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/stlink_org:v1.0.0",
        "axemsolutions/cpputest:latest",
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/make_gnu_arm:v0.1.0", 
        "axemsolutions/make_gnu_arm:v1.1.0",
        "axemsolutions/jlink:latest",
    ]
    test_registry_images = [
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/cmake:latest",
        "axemsolutions/llvm:latest",
        "axemsolutions/pemicro:latest",
        "axemsolutions/unity:latest"
    ]
    mock_read_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_read_deserialized_dev_env_org_json.return_value = json.loads(fake_data.dev_env_org_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_tool_images.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", "org_only_env"])

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_container_engine.get_local_tool_images.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_tools = [
        ["build system", "axemsolutions/cmake:latest", "Image is available in the registry."],
        ["toolchain", "axemsolutions/llvm:latest", "Image is available in the registry."],
        ["debugger", "axemsolutions/pemicro:latest", "Image is available in the registry."],
        ["deployer", "axemsolutions/pemicro:latest", "Image is available in the registry."],
        ["test framework", "axemsolutions/unity:latest", "Image is available in the registry."],
    ]
    assert get_expected_table(expected_tools) == runner_result.stdout
"""
Shared fixtures and configuration for Tablet2LaTeX tests.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock config file with valid configuration."""
    config_path = Path(temp_dir) / "config.ini"
    config_content = """[API]
provider = openai
openai_api_key = test_api_key
openai_model = gpt-4o
openai_base_url = https://api.openai.com/v1
ollama_base_url = http://localhost:11434/v1
ollama_model = llava
llamacpp_base_url = http://localhost:8080/v1
llamacpp_model = llava

[Canvas]
width = 800
height = 600

[LLM]
max_tokens = 1000
prompt = Convert the handwritten text to LaTeX.

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture
def mock_config_file_ollama(temp_dir):
    """Create a mock config file with Ollama provider."""
    config_path = Path(temp_dir) / "config_ollama.ini"
    config_content = """[API]
provider = ollama
openai_api_key = 
ollama_base_url = http://localhost:11434/v1
ollama_model = llava

[Canvas]
width = 1024
height = 768

[LLM]
max_tokens = 2000

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture
def mock_config_file_llamacpp(temp_dir):
    """Create a mock config file with LlamaCpp provider."""
    config_path = Path(temp_dir) / "config_llamacpp.ini"
    config_content = """[API]
provider = llamacpp
llamacpp_base_url = http://localhost:8080/v1
llamacpp_model = llava

[Canvas]
width = 512
height = 384

[LLM]
max_tokens = 500

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture
def mock_config_file_invalid_provider(temp_dir):
    """Create a mock config file with invalid provider."""
    config_path = Path(temp_dir) / "config_invalid.ini"
    config_content = """[API]
provider = invalid_provider

[Canvas]
width = 800
height = 600

[LLM]
max_tokens = 1000

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture
def mock_config_file_missing_section(temp_dir):
    """Create a mock config file with missing required section."""
    config_path = Path(temp_dir) / "config_missing.ini"
    config_content = """[API]
provider = openai

[Canvas]
width = 800
height = 600

[LLM]
max_tokens = 1000

"""
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture
def mock_config_file_invalid_numbers(temp_dir):
    """Create a mock config file with invalid numeric values."""
    config_path = Path(temp_dir) / "config_invalid_nums.ini"
    config_content = """[API]
provider = openai

[Canvas]
width = invalid
height = 600

[LLM]
max_tokens = -100

[Shortcuts]
tool_pen = <Control>c
tool_eraser = <Control>e
clear_canvas = <Control>d
submit = <Control>s
"""
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    # Store original values
    orig_xdg_home = os.environ.get("XDG_CONFIG_HOME")

    yield

    # Restore original values
    if orig_xdg_home is not None:
        os.environ["XDG_CONFIG_HOME"] = orig_xdg_home
    elif "XDG_CONFIG_HOME" in os.environ:
        del os.environ["XDG_CONFIG_HOME"]

from pathlib import Path

import pytest

Resource_Dir = Path(__file__).parent / '../resources/'
Example_Dir = Path(__file__).parent / '../examples/'


@pytest.fixture
def resource_dir():
    return Path(__file__).parent / '../resources/'


@pytest.fixture
def example_dir():
    return Path(__file__).parent / '../examples/'
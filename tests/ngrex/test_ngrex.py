import pytest

from radtext.models.neg import ngrex


def test_compile():
    p = '@'
    with pytest.raises(TypeError):
        ngrex.compile(p)

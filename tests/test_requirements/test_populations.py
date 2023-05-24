"""Requirements module for evaluators."""
# pylint: disable=redefined-outer-name


def test_names_are_string(populations):
    """Test spawn population returns a string identifier (name)."""
    for name in populations:
        assert isinstance(name, str)

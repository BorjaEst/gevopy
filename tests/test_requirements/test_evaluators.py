"""Requirements module for evaluators."""
# pylint: disable=redefined-outer-name
from inspect import signature


def test_are_callable(evaluators):
    """Test evaluators are callable with arity 1"""
    for evaluator in evaluators:
        assert callable(evaluator)
        assert len(signature(evaluator).parameters) == 1

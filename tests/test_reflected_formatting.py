import pytest
from flask_babel.speaklater import LazyString


class ReflectedTemplate(str):
    def __mod__(self, value):
        return NotImplemented


def test_direct_reflected_formatting():
    assert LazyString(lambda: "world").__rmod__("Hello %s!") == "Hello world!"


def test_percent_operator_can_use_reflected_formatting():
    assert (
        ReflectedTemplate("Hello %s!") % LazyString(lambda: "world") == "Hello world!"
    )


def test_reflected_formatting_evaluates_when_used():
    calls = []
    value = LazyString(lambda: calls.append(True) or "world")
    assert calls == []
    assert ReflectedTemplate("%s") % value == "world"
    assert calls == [True]


def test_reflected_formatting_preserves_format_errors():
    with pytest.raises(TypeError):
        ReflectedTemplate("%d") % LazyString(lambda: "world")

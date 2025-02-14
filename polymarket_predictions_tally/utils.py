from typing import Any, Callable, TypeVar


def indent_lines(str_: str, indent_level: int = 1) -> str:
    return "\n".join([indent_level * "\t" + line for line in str_.split("\n")])


S = TypeVar("S")


def assert_fails(f: Callable[..., S], *args: Any, **kwargs: Any):
    try:
        f(*args, **kwargs)
        raise AssertionError("Expected function to fail, but it succeeded.")
    except:
        pass

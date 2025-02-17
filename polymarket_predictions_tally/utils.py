from datetime import datetime
from typing import Any, Callable, Optional, Type, TypeVar


def indent_lines(str_: str, indent_level: int = 1) -> str:
    return "\n".join([indent_level * "\t" + line for line in str_.split("\n")])


S = TypeVar("S")


def assert_fails(f: Callable[..., S], *args: Any, **kwargs: Any):
    try:
        f(*args, **kwargs)
        raise AssertionError("Expected function to fail, but it succeeded.")
    except:
        pass


def assert_fails_with_exception(
    f: Callable[..., S],
    *args: Any,
    expected_exception: Optional[Type[BaseException]] = None,
    **kwargs: Any,
) -> None:
    """
    Assert that calling f(*args, **kwargs) raises an exception.

    If expected_exception is provided, the raised exception must be an instance
    of expected_exception. Otherwise, any exception will pass the test.

    Args:
        f: A callable.
        *args: Positional arguments for the callable.
        expected_exception: The expected exception type.
        **kwargs: Keyword arguments for the callable.

    Raises:
        AssertionError: If no exception is raised, or if an exception of an unexpected
                        type is raised.
    """
    try:
        f(*args, **kwargs)
    except Exception as e:
        if expected_exception is not None and not isinstance(e, expected_exception):
            raise AssertionError(
                f"Expected exception {expected_exception.__name__}, "
                f"but got {type(e).__name__}"
            ) from e
        return  # Exception raised as expected
    raise AssertionError("Expected function to fail, but it succeeded.")


def parse_datetime(dt_str: str) -> datetime:
    """Parse a datetime string, handling cases with or without microseconds."""
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unrecognized datetime format: {dt_str}")


def load_sql_query(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()

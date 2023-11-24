from functools import partial
from subprocess import PIPE, run
from textwrap import dedent

import pytest

from flake8_annotations import error_codes
from testing.helpers import check_source

ERR = partial(error_codes.ANN401, lineno=3)

TEST_CASES = (
    (
        dedent(
            """\
            from typing import Any

            def foo(a: Any) -> None:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            from typing import Any

            def foo(a: int) -> Any:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            import typing as t

            def foo(a: t.Any) -> None:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            import typing as t

            def foo(a: int) -> t.Any:
                ...
            """
        ),
    ),
)


@pytest.mark.parametrize(("src",), TEST_CASES)
def test_dynamic_typing_errors(src: str) -> None:
    found_errors = list(check_source(src))
    assert len(found_errors) == 1

    _, _, err_msg, _ = found_errors[0]
    assert "ANN401" in err_msg


INP = dedent(
    """\
    import typing
    def foo(a: typing.Any) -> None:
        ...
    """
)

RUN_PARTIAL = partial(run, stdout=PIPE, input=INP, encoding="ascii")


def test_ANN401_ignored_default() -> None:
    p = RUN_PARTIAL(["flake8", "-"])

    assert "ANN401" not in p.stdout


def test_ANN401_fire_when_selected() -> None:
    p = RUN_PARTIAL(["flake8", "--extend-select=ANN401", "-"])

    assert "ANN401" in p.stdout


STARG_CASES = (
    (
        dedent(
            """\
            from typing import Any

            def foo(*a: Any) -> None:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            from typing import Any

            def foo(**a: Any) -> None:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            from typing import Any

            def foo(a: int, *b: Any, c: int) -> None:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            import datetime as dt
            from typing import Any

            def foo(a: int, *b: Any, c: dt.datetime) -> None:
                ...
            """
        ),
    ),
    (
        dedent(
            """\
            from typing import Any

            def foo(a: int, *, b: int, **c: Any) -> None:
                ...
            """
        ),
    ),
)


@pytest.mark.parametrize(("src",), STARG_CASES)
def test_ignore_stargs(src: str) -> None:
    found_errors = list(check_source(src, allow_star_arg_any=True))
    assert len(found_errors) == 0

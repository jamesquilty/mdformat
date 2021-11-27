from __future__ import annotations

import functools
from pathlib import Path
from typing import Mapping

from mdformat._compat import tomllib

DEFAULT_OPTS = {
    "wrap": "keep",
    "number": False,
    "end_of_line": "lf",
    "primary_bullet_list_marker": "-",
    "secondary_bullet_list_marker": "*",
    "primary_ordered_list_marker": ".",
    "secondary_ordered_list_marker": ")",
    "thematic_break_character": "_",
    "thematic_break_width": 70,
    "escape_square_brackets": True,
    "entity_substitution": True,
}


class InvalidConfError(Exception):
    """Error raised on invalid TOML configuration.

    Will be raised on:
    - invalid TOML
    - invalid conf key
    - invalid conf value
    """


@functools.lru_cache()
def read_toml_opts(conf_dir: Path) -> Mapping:
    conf_path = conf_dir / ".mdformat.toml"
    if not conf_path.is_file():
        parent_dir = conf_dir.parent
        if conf_dir == parent_dir:
            return {}
        return read_toml_opts(parent_dir)

    with open(conf_path, "rb") as f:
        try:
            toml_opts = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise InvalidConfError(f"Invalid TOML syntax: {e}")

    _validate_keys(toml_opts, conf_path)
    _validate_values(toml_opts, conf_path)

    return toml_opts


def _validate_values(opts: Mapping, conf_path: Path) -> None:
    if "wrap" in opts:
        wrap_value = opts["wrap"]
        if not (
            (isinstance(wrap_value, int) and wrap_value > 1)
            or wrap_value in {"keep", "no"}
        ):
            raise InvalidConfError(f"Invalid 'wrap' value in {conf_path}")
    if "end_of_line" in opts:
        if opts["end_of_line"] not in {"crlf", "lf", "keep"}:
            raise InvalidConfError(f"Invalid 'end_of_line' value in {conf_path}")
    if "number" in opts:
        if not isinstance(opts["number"], bool):
            raise InvalidConfError(f"Invalid 'number' value in {conf_path}")
    if "primary_bullet_list_marker" in opts and opts[
        "primary_bullet_list_marker"
    ] not in {"*", "+", "-"}:
        raise InvalidConfError(
            f"Invalid 'primary_bullet_list_marker' value in {conf_path}"
        )
    if "secondary_bullet_list_marker" in opts and opts[
        "secondary_bullet_list_marker"
    ] not in {"*", "+", "-"}:
        raise InvalidConfError(
            f"Invalid 'secondary_bullet_list_marker' value in {conf_path}"
        )
    # if "primary_ordered_list_marker" in opts and opts[
    #     "primary_ordered_list_marker"
    # ] not in {".", ")"}:
    #     raise InvalidConfError(
    #         f"Invalid 'primary_ordered_list_marker' value in {conf_path}"
    #     )
    # if "secondary_ordered_list_marker" in opts and opts[
    #     "secondary_ordered_list_marker"
    # ] not in {".", ")"}:
    #     raise InvalidConfError(
    #         f"Invalid 'secondary_ordered_list_marker' value in {conf_path}"
    #     )
    # if "thematic_break_width" in opts and 3 < opts["thematic_break_width"] > 120:
    #     raise InvalidConfError(
    #         f"Invalid 'thematic_break_width' value in {conf_path} "
    #         f"(must be between 3 and 120)"
    #     )
    # if "escape_square_brackets" in opts and opts["escape_square_brackets"] not in {
    #     True,
    #     False,
    # }:
    #     raise InvalidConfError(
    #         f"Invalid 'escape_square_brackets' value in {conf_path}"
    #         f"(must be 'true' or 'false')"
    #     )


def _validate_keys(opts: Mapping, conf_path: Path) -> None:
    for key in opts:
        if key not in DEFAULT_OPTS:
            raise InvalidConfError(
                f"Invalid key {key!r} in {conf_path}."
                f" Keys must be one of {set(DEFAULT_OPTS)}."
            )

def indent_lines(str_: str, indent_level: int = 1) -> str:
    return "\n".join([indent_level * "\t" + line for line in str_.split("\n")])

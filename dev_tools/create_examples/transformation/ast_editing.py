import re
import textwrap

import libcst as cst


def update_function_docstrings(code: str, examples: dict[str, str]) -> str:
    """Add or update the example section in selected function docstrings."""
    module = cst.parse_module(code)
    return module.visit(DocstringTransformer(examples)).code


class DocstringTransformer(cst.CSTTransformer):
    """Add, append, or replace example sections in function docstrings."""

    def __init__(self, examples: dict[str, str]) -> None:
        self.examples = examples

    def leave_FunctionDef(  # noqa: N802
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        example = self.examples.get(original_node.name.value, "")
        if not example:
            return updated_node

        body = updated_node.body
        if isinstance(body, cst.IndentedBlock):
            statements = body.body
            docstring = _get_docstring(statements)
            if docstring is None:
                statements = (_make_docstring(example), *statements)
            else:
                index, statement, value = docstring
                new_value = _update_docstring(value.raw_value, example)
                replacement = statement.with_changes(
                    body=(cst.Expr(value=cst.SimpleString(new_value)),)
                )
                statements = (*statements[:index], replacement, *statements[index + 1 :])

            return updated_node.with_changes(body=body.with_changes(body=statements))

        statements = tuple(cst.SimpleStatementLine(body=(statement,)) for statement in body.body)
        return updated_node.with_changes(
            body=cst.IndentedBlock(body=(_make_docstring(example), *statements), indent="    ")
        )


def _get_docstring(
    statements: tuple[cst.BaseStatement, ...],
) -> tuple[int, cst.SimpleStatementLine, cst.SimpleString] | None:
    if not statements or not isinstance(statements[0], cst.SimpleStatementLine):
        return None

    statement = statements[0]
    if len(statement.body) != 1 or not isinstance(statement.body[0], cst.Expr):
        return None

    value = statement.body[0].value
    if not isinstance(value, cst.SimpleString):
        return None

    return 0, statement, value


def _make_docstring(example: str) -> cst.SimpleStatementLine:
    value = _update_docstring("", example)
    return cst.SimpleStatementLine(body=(cst.Expr(value=cst.SimpleString(value)),))


def _update_docstring(docstring: str, example: str) -> str:
    example = _format_example(example)
    pattern = (
        r"(?ms)^[ \t]*Papertrail examples:\n.*?\n[ \t]*::"
        r"|^[ \t]*\.\. code-block:: python\n.*?\n[ \t]*::"
    )
    matches = list(re.finditer(pattern, docstring))
    if matches:
        first = matches[0]
        sections = [docstring[: first.start()], example]
        end = first.end()
        for match in matches[1:]:
            sections.append(docstring[end : match.start()])
            end = match.end()
        sections.append(docstring[end:])
        new_doc = "".join(sections)
    else:
        new_doc = f"{docstring}\n\n{example}"

    return f'"""{new_doc.strip()}\n        """'


def _format_example(example: str) -> str:
    lines = example.splitlines(keepends=True)
    if not lines:
        return ""

    return textwrap.indent("".join(lines), "        ", predicate=lambda line: bool(line.strip()))

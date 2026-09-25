from collections import defaultdict

import black

from ..collection.record import ExampleRecord  # noqa: TID252


def collect_example_strs(examples: list[dict]) -> dict[str, dict[str, list[str]]]:
    fn_examples = defaultdict(_inner)

    for data in examples:
        ex = ExampleRecord(**data)

        if ex.returned != ex.expected:
            continue

        fn_examples[ex.src_file][ex.fn_name].append(example_to_str(ex))

    return {k: dict(v) for k, v in fn_examples.items()}


def _inner() -> defaultdict:
    return defaultdict(list)


def example_to_str(example: ExampleRecord) -> str:
    sig = ", ".join(
        part
        for part in (
            ", ".join(map(str, example.args)),
            ", ".join(f"{k}={v}" for k, v in example.kwargs.items()),
        )
        if part
    )
    expr = f"{example.ent_repr}({sig}) == {example.returned}"
    formatted = black.format_str(expr, mode=black.Mode())
    lines = formatted.rstrip().splitlines()
    doctest = "\n".join(
        f"{'    >>>' if i == 0 else '    ...'} {line}" for i, line in enumerate(lines)
    )
    return f"{doctest}\n    True"


def reduce_examples_to_example_str(
    fn_examples: dict[str, dict[str, list[str]]],
) -> dict[str, dict[str, str]]:
    return {
        path: {k: ".. code-block:: python\n\n" + "\n\n".join(v) + "\n::" for k, v in fn.items()}
        for path, fn in fn_examples.items()
    }

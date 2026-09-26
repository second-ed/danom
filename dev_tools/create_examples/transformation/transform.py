import json
from pathlib import Path

from .ast_editing import update_function_docstrings
from .format_examples import collect_example_strs, reduce_examples_to_example_str


def update_modified_docstrings(examples_cache_path: Path) -> None:
    examples = json.loads(examples_cache_path.read_text())
    reduced_examples = reduce_examples_to_example_str(collect_example_strs(examples))

    for path, module_examples in reduced_examples.items():
        code = Path(path).read_text()
        new_code = update_function_docstrings(code, module_examples)
        if new_code != code:
            Path(path).write_text(new_code)

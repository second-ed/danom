import inspect
import re
import sys
from pathlib import Path

import attrs

from danom import (
    Result,
    Stream,
    all_of,
    any_of,
    compose,
    identity,
    invert,
    new_type,
    safe,
    safe_method,
)


@attrs.define(frozen=True)
class ReadmeDoc:
    name: str
    sig: str = attrs.field(converter=str)
    doc: str

    def to_readme(self) -> str:
        docs = strip_doc(self.doc)
        return "\n".join([f"### `{self.name}`", f"```python\n{self.name}{self.sig}\n```", docs])


def create_readme_lines() -> str:
    readme_lines = []

    for ent in [Stream, Result]:
        readme_lines.append(f"## {ent.__name__}")
        readme_lines.append(strip_doc(ent.__doc__))
        readme_docs = [
            ReadmeDoc(f"{ent.__name__}.{k}", inspect.signature(v), v.__doc__)
            for k, v in inspect.getmembers(ent, inspect.isroutine)
            if not k.startswith("_")
        ]
        readme_lines.extend([entry.to_readme() for entry in readme_docs])

    for fn in [safe, safe_method, compose, all_of, any_of, identity, invert, new_type]:
        readme_lines.append(f"## {fn.__name__}")
        readme_docs = [ReadmeDoc(f"{fn.__name__}", inspect.signature(fn), fn.__doc__)]
        readme_lines.extend([entry.to_readme() for entry in readme_docs])
    return "\n\n".join(readme_lines)


def update_readme(new_docs: str, readme_path: str = "./README.md") -> None:
    readme_path = Path(readme_path)
    readme_txt = readme_path.read_text(encoding="utf-8")
    pattern = r"(# API Reference)(.*?)(::)"
    updated_readme = re.sub(pattern, rf"\1\n\n{new_docs}\n\3", readme_txt, flags=re.DOTALL)
    if readme_txt != updated_readme:
        readme_path.write_text(updated_readme)
        return 1
    return 0


def strip_doc(doc: str) -> str:
    return "\n".join([line.strip() for line in doc.splitlines()])


if __name__ == "__main__":
    sys.exit(update_readme(create_readme_lines()))

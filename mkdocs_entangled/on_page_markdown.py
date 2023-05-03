from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import re
import tempfile
import subprocess
import sys

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

from .config import EntangledConfig
from .properties import read_properties, Id, Attribute, Class
from . import mawk


@dataclass
class EntangledFilter(mawk.RuleSet):
    add_title: bool = True
    build_artifacts: bool = True

    _collect_make_script: bool = False
    _ignore: bool = False

    @mawk.on_match(r"~~~markdown")
    def start_ignore(self, m):
        self._ignore = True
        return [m[0]]
    
    @mawk.on_match(r"~~~")
    def stop_ignore(self, m):
        self._ignore = False
        return [m[0]]

    @mawk.on_match(r"(\s*)``` *\{([^}]*)\}")
    def open_code_block(self, m: re.Match) -> Optional[list[str]]:
        if self._ignore:
            return None

        indent = m[1]
        props = list(read_properties(m[2]))
        
        ids = [p.value for p in props if isinstance(p, Id)]
        filenames = [p.value for p in props if isinstance(p, Attribute) and p.key == "file"]

        if self.add_title:
            title = None
            if len(ids) == 1 and len(filenames) == 1:
                title = f"#{ids[0]} / file: {filenames[0]}"
            elif len(ids) == 1:
                title = f"#{ids[0]}"
            elif len(filenames) == 1:
                title = f"file: {filenames[0]}"
            elif len(ids) > 1 or len(filenames) > 1:
                title = f"error: ambiguous code block title"

            if title is not None:
                props.append(Attribute("title", title))
        
        if self.build_artifacts and Class("build-artifact") in props:
            self._collect_make_script = True
            self._make_script: list[str] = []
            self._make_props = props
            self._indent = indent

        prop_str = " ".join(str(p) for p in props)
        return [f"{indent}``` {{{prop_str}}}"]

    @mawk.on_match(r"\s*```\s*$")
    def close_code_block(self, m: re.Match) -> Optional[list[str]]:
        if not self._ignore and self._collect_make_script:
            self._collect_make_script = False
            script = "\n".join(self._make_script)
            with tempfile.TemporaryDirectory() as _tmpdir:
                tmpdir = Path(_tmpdir)
                with open(tmpdir / "Makefile", "w") as makefile:
                    makefile.write(script)
                subprocess.run(["make", "-f", str(tmpdir / "Makefile")])
        return None

    @mawk.always
    def add_line_to_script(self, line: str) -> Optional[list[str]]:
        if not self._ignore and self._collect_make_script:
            self._make_script.append(line.removeprefix(self._indent))
        return None


def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> str:
    result = EntangledFilter().run(markdown)
    return result


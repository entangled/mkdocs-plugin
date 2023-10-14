from typing import Optional
from dataclasses import dataclass
import re

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

from .properties import read_properties, Id, Attribute
import mawk


@dataclass
class EntangledFilter(mawk.RuleSet):
    add_title: bool = True
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
        
        prop_str = " ".join(str(p) for p in props)
        return [f"{indent}``` {{{prop_str}}}"]

    @mawk.on_match(r"\s*```\s*$")
    def close_code_block(self, m: re.Match) -> Optional[list[str]]:
        return None


def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> str:
    result = EntangledFilter().run(markdown)
    return result


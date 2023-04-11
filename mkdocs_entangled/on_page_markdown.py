import re

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

from .config import EntangledConfig
from .properties import read_properties, Id, Attribute
from . import mawk


@mawk.on_match("``` *\\{([^}]*)\\}")
def modify_properties(m: re.Match) -> list[str]:
    props = list(read_properties(m[1]))
    
    ids = [p.value for p in props if isinstance(p, Id)]
    filenames = [p.value for p in props if isinstance(p, Attribute) and p.key == "file"]

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
    return [f"``` {{{prop_str}}}"]


def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> str:
    return mawk.run([modify_properties], markdown)


from collections.abc import Iterable, Callable
from functools import partial, reduce
from pathlib import Path
from textwrap import indent
from itertools import chain

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

from entangled.document import ReferenceMap, Content, PlainText, ReferenceId, CodeBlock, document_to_text
from entangled.properties import get_attribute, Id, Attribute, Class
from entangled.hooks import get_hooks
from entangled.config import config
from repl_session import read_session

config.read()

# The Entangled config needs to be read before importing the Markdown reader
# This is very bad I know, and should be fixed in some future version.
from entangled.markdown_reader import read_markdown_string


type ContentFilter = Callable[[ReferenceMap, Content], Iterable[Content]]
type CodeBlockFilter = Callable[[ReferenceMap, ReferenceId], Iterable[Content]]


def codeblock_filter(f: CodeBlockFilter) -> ContentFilter:
    def _foo(rm: ReferenceMap, c: Content) -> Iterable[Content]:
        match c:
            case PlainText():
                return [c]
            case ReferenceId():
                return f(rm, c)
    return _foo


def iter_bind[T, U](lst: Iterable[T], f: Callable[[T], Iterable[U]]) -> Iterable[U]:
    return chain(*map(f, lst))


def compose_filter(a: ContentFilter, b: ContentFilter) -> ContentFilter:
    def _joined(rm: ReferenceMap, c: Content) -> Iterable[Content]:
        return iter_bind(partial(a, rm)(c), partial(b, rm))
    return _joined


def compose_filters(*args: ContentFilter) -> ContentFilter:
    return reduce(compose_filter, args, lambda _, c: [c])


def read_markdown(text: str) -> tuple[ReferenceMap, list[Content]]:
    hooks = get_hooks()
    return read_markdown_string(text, hooks=hooks)


@codeblock_filter
def add_title(reference_map: ReferenceMap, r: ReferenceId) -> list[Content]:
    """
    Changes the `open_line` member of a `CodeBlock` to reflect accepted
    MkDocs syntax, adding a `title` attribute.
    """
    codeblock: CodeBlock = reference_map.get_codeblock(r)

    ids = [p.value for p in codeblock.properties if isinstance(p, Id)]
    classes = [p.value for p in codeblock.properties if isinstance(p, Class)]
    filenames = [p.value for p in codeblock.properties if isinstance(p, Attribute) and p.key == "file"]

    title = None
    if len(ids) == 1 and len(filenames) == 1:
        title = f"#{ids[0]} / file: {filenames[0]}"
    elif len(ids) == 1:
        title = f"#{ids[0]}"
    elif len(filenames) == 1:
        title = f"file: {filenames[0]}"
    elif len(ids) > 1 or len(filenames) > 1:
        title = "error: ambiguous code block title"

    open_line = "```"
    if classes:
        language_id = classes[0]
        open_line += language_id

    if ids or classes or title:
        open_line += " {"

        if ids:
            open_line += str(Id(ids[0]))

        for c in classes[1:]:
            open_line += " " + str(Class(c))

        if title:
            open_line += " " + str(Attribute("title", title))

        open_line += "}"

    codeblock.open_line = open_line
    return [r]


@codeblock_filter
def include_repl_output(reference_map: ReferenceMap, r: ReferenceId) -> list[Content]:
    """
    Takes any codeblock that has the `repl` class and append its pre-computed output.
    """
    codeblock: CodeBlock = reference_map.get_codeblock(r)
    if Class("repl") not in codeblock.properties:
        return [r]

    first: CodeBlock = next(iter(reference_map.by_name(r.name)))
    session_filename = get_attribute(first.properties, "session")
    assert session_filename is not None
    session_path: Path = Path(session_filename)
    assert session_path.exists()
    session_output_path: Path = session_path.with_suffix(".out.json")
    assert session_output_path.exists()

    session = read_session(session_output_path.open("r"))
    command = session.commands[r.ref_count]

    if not command.output:
        return [r]

    output: str
    if command.output_type == "text/plain":
        output = indent(f"\n``` {{.text .output}}\n{command.output}\n```", codeblock.indent)
    else:
        output = indent(f"\n**unknown MIME type: {command.output_type}**", codeblock.indent)

    return [r, PlainText(output)]


def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> str:
    reference_map, content = read_markdown(markdown)
    filtered_content = iter_bind(content, partial(compose_filters(add_title, include_repl_output), reference_map))
    return document_to_text(reference_map, filtered_content)

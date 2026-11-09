from functools import partial
from pathlib import Path
from textwrap import dedent

import pytest
from entangled.interface import Context
from mkdocs.commands.build import build
from mkdocs.config import load_config

from mkdocs_entangled.on_page_markdown import add_title, document_to_text, iter_bind, read_single_markdown


MARKDOWN = dedent("""\
    # Test page

    ``` {.python file=hello.py}
    <<hello-world>>
    ```

    ``` {.python #hello-world}
    print("Hello, World!")
    ```
    """)

MKDOCS_YML = dedent("""\
    site_name: Test
    plugins:
      - entangled
    markdown_extensions:
      - attr_list
      - pymdownx.superfences
      - pymdownx.highlight
    """)


def test_add_title_markdown() -> None:
    refs, content = read_single_markdown(Context(), MARKDOWN)
    result = document_to_text(refs, iter_bind(content, partial(add_title, refs)))
    assert '```python { title="file: hello.py"}' in result
    assert '```python {#hello-world title="#hello-world"}' in result


@pytest.fixture
def site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Build a minimal MkDocs project with the entangled plugin, return the site dir."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text(MARKDOWN)
    (tmp_path / "mkdocs.yml").write_text(MKDOCS_YML)
    (tmp_path / "entangled.toml").write_text('version = "2.0"\n')
    # The plugin reads entangled.toml from the working directory
    monkeypatch.chdir(tmp_path)

    config = load_config(config_file=str(tmp_path / "mkdocs.yml"))
    build(config)
    return tmp_path / "site"


def test_build_renders_titles(site: Path) -> None:
    html = (site / "index.html").read_text()
    assert '<span class="filename">file: hello.py</span>' in html
    assert '<span class="filename">#hello-world</span>' in html

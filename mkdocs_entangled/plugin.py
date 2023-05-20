import logging
import mkdocs
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

from entangled.commands import sync
from entangled.main import configure

from .on_page_markdown import on_page_markdown
from .config import EntangledConfig

class EntangledPlugin(mkdocs.plugins.BasePlugin[EntangledConfig]):
    def on_pre_build(self, config: MkDocsConfig):
        configure()
        logging.info("Running `entangled sync`")
        sync()
        
    def on_page_markdown(self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files):
        return on_page_markdown(markdown, page=page, config=config, files=files)

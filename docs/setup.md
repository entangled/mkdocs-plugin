# Setup instructions for MkDocs with Entangled
If you'd like to use Entangled together with MkDocs, here's an opiniated guide.

## Python and MkDocs
Start with an empty project folder, say `my-awesome-project`.

```sh
mkdir my_awesome_project
cd my_awesome_project
git init
```

You may want to setup a virtual environment to install MkDocs into. Even if your project is not Python related, it pays to have a reproducible build environment for your documentation. I use [`uv`](https://docs.astral.sh/uv/) to manage my environments.

```bash
uv init --bare
uv add -D mkdocs mkdocs-material entangled-cli mkdocs-entangled-plugin
uv sync
source .venv/bin/activate
```

Now you have created a virtual environment using UV and activated it (alas there is no `uv shell` command that I know of).
Next we initialize, configure, and run MkDocs.

```sh
mkdocs new .
```

Now edit `mkdocs.yml` to your own settings, here's an example.

```yaml
site_name: My Awesome Project
site_url: https://joeplummer.github.io/my-awesome-project
repo_url: https://github.com/joeplummer/my-awesome-project

plugins:
  - entangled

markdown_extensions:
  - attr_list
  - pymdownx.superfences

theme:
  name: material
```

This sets the title, repo name and a toggle for dark mode viewing. the `entangled` plugin expects the `attr_list` and `pymdownx.superfences` markdown extensions to be enabled.
Make sure to check out [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) for more documentation on configuring MkDocs with Material.

```sh
mkdocs serve
```

This will start a build loop and web server. That means that every time one of the source files change, MkDocs will compile the Markdown to HTML and the browser will automatically refresh.

## Setup Entangled
Entangled will work without any additional configuration in `entangled.toml`. The default config monitors the entire source repository for Markdown files. Files that are extracted from the Markdown are also watched for changes. If you'd like to limit the scope of Markdown files that are monitored, you can set `watch_list` to a list of glob patterns. For MkDocs projects it makes sense to set `watch_list = [ "docs/**/*.md" ]`.

We will also demo the `repl` hook for Entangled later on.

The complete configuration then looks like this:

``` {.toml file=examples/entangled.toml}
version = "2.0"
watch_list = ["docs/**/*.md"]
hooks = ["repl"]

<<repl-config>>
```

## Extras
Some extras.

### Syntax Highlighting
Add the following to the `markdown_extensions` section in `mkdocs.yml`:

```yaml
markdown_extensions:
  # <<your old settings are still here>>
  # ...
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
```

### Evaluating a REPL session
When you write documentation or teaching material it can be nice to automatically evaluate commands in a REPL and show the results in your rendered output. Entangled ships with a command-line tool `repl-session` that evaluates a series of commands in a configured REPL. Both input and output are JSON data.
Entangled contains a hook that integrates with `repl-session`.

For each language you need to configure the REPL in `entangled.toml` in the `[hook.repl.config.<language>]` section. For example,

``` {toml #repl-config}
[hook.repl.config.Lua]
command = "lua"
first_prompt = "> "
change_prompt = '_PROMPT = "{key}> "; _PROMPT2 = "{key}+ "'
prompt = "{key}> "
continuation_prompt = "{key}\\+ "
strip_ansi = true
```

Each repl block must be attached to a session, which is the JSON file to which the session is written. It is the responsibility of the user to make sure, with whatever build system tool (say GNU Make or Brei), that the resulting JSON file is passed through `repl-session` to a file in the same directory with the `out.json` extension. This way, the REPL session will only be rerun when the session file changes.

Did you know that Lua supports tail-call elimination? We can define a factorial function,

``` {.lua .repl #lua-repl session=examples/lua-session.json}
function fac(n, m)
    if m == nil then
        return fac(n, 1)
    end
    if n == 0 then
        return m
    else
        return fac(n-1, m*n)
    end
end
```

and this runs in constant stack space!

``` {.lua .repl #lua-repl}
fac(63)
```

### Equations using Mathjax
A common requirement is to have support for equations. Add the following to your `mkdocs.yml`

```yaml
markdown_extensions:
  # <<your old settings are still here>>
  # ...
  - pymdownx.arithmatex:
      generic: true

extra_javascript:
  - js/mathjax.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

You'll also need to create `docs/js/mathjax.jl`.

```js
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    tags: 'ams'
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

document$.subscribe(() => {
  MathJax.typesetPromise();
})
```

### Dark mode
You can enable a dark-mode toggle by adding to your `mkdocs.yml`

```yaml
theme:
  name: material
  palette:
    # Palette toggle for light mode
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode

    # Palette toggle for dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
```

### Github Actions
You may want to use Github Actions to deploy the website. I use the following `.github/workflows/deploy-pages.yaml`:

<details><summary>Deploy Pages action</summary>

Note from two years later: Github Actions are extraordinarily fickle and require constant maintenance. Always make sure that you update to the newest versions. This version is from October 2025:

```yaml
name: Deploy pages

# Controls when the workflow will run
on:
  # Triggers the workflow on push or pull request events but only for the "main" branch
  push:
    branches: ["main"]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

# Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
# However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
concurrency:
  group: "pages"
  cancel-in-progress: false

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  build:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync

      - name: Run MkDocs
        run: uv run mkdocs build

      - name: Configure GitHub Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v4
        with:
          path: "site"

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

</details>

## Commit
Don't forget to create a `README.md`, `LICENSE`, and later on a `CITATION.cff`.
A fresh Entangled/MkDocs project should have the following files:

```
.
├── CITATION.cff
├── docs
│   ├── index.md
│   └── js
│       └── mathjax.js
├── entangled.toml
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
└── README.md
```

Create a home for your new project and push.

```sh
git add .
git commit -m 'initial commit'
git remote add origin git@github.com:johndoe/my-awesome-project.git
git push -u origin main
```

## Resources

- [mkdocs-macros](https://mkdocs-macros-plugin.readthedocs.io/en/latest/) is a plugin for using Jinja syntax to create macros. This also let's you `{% include "..." %}` external files.
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) is a nice theme for MkDocs, and has many features for non-standard elements.
- [mkdocs-bibtex](https://github.com/shyamd/mkdocs-bibtex/) adds citation management through bibtex.

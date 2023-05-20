# Setup instructions for MkDocs with Entangled
If you'd like to use Entangled together with MkDocs, here's an opiniated guide (if you have differing opinions, you'll know howto adapt). 

## Python and MkDocs
Start with an empty project folder, say `my-awesome-project`.

```sh
mkdir my_awesome_project
cd my_awesome_project
git init
```

You may want to setup a virtual environment to install MkDocs into. Even if your project is not Python related, it pays to have a reproducible build environment for your documentation. I use [Poetry](https://python-poetry.org/) to manage my environments.

```sh
poetry init
# <<follow the gentle instructions>>
poetry add -D mkdocs mkdocs-material entangled-cli[rich] mkdocs-entangled-plugin
poetry shell
```

Using virtual environments will take up some disk space. With these moderate requirements however, we're still under 200 MB.

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
  - pymdownx.superfences

theme:
  name: material
```

This sets the title, repo name and a toggle for dark mode viewing. the `entangled` plugin needs `pymdownx.superfences` to be enabled.
Make sure to check out [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) for more documentation on configuring MkDocs with Material.

```sh
mkdocs serve
```

This will start a build loop and web server. That means that every time one of the source files change, MkDocs will compile the Markdown to HTML and the browser will automatically refresh.

## Setup Entangled
Entangled will work without any additional configuration in `entangled.toml`. The default config monitors the entire source repository for Markdown files. Files that are extracted from the Markdown are also watched for changes. If you'd like to limit the scope of Markdown files that are monitored, you can set `watch_list` to a list of glob patterns. For MkDocs projects it makes sense to set `watch_list = [ "docs/**/*.md" ]`.

To enable building artifacts add the `build` hook, by setting `hooks = ["build"]`.

The complete configuration then looks like this:

``` {.toml file=examples/entangled.toml}
version = "2.0"
watch_list = ["docs/**/*.md"]
hooks = ["build"]
```

Entangled runs as a pre-build action in MkDocs. So, you may want to add your generated source files in the watch list of MkDocs. Assuming your source files are in `./src`:

```yaml
watch:
  - docs
  - src
```

## Extras
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

```yaml
name: Deploy Pages

# Controls when the workflow will run
on:
  # Triggers the workflow on push or pull request events but only for the "main" branch
  push:
    branches: [ "main" ]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v3

      - name: Install 
        run: |
          pip install poetry
          poetry install

      - name: Generate site
        run: poetry run mkdocs build
  
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: 'site'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

</details>

## Commit
Don't forget to create a `README.md`, `LICENSE`, and later on a `CITATION.cff`. You may want to add `poetry.lock` to `.gitignore`.
You should be good to go! A fresh Entangled/MkDocs project should have the following files:

```
.
├── CITATION.cff
├── docs
│   ├── index.md
│   └── js
│       └── mathjax.js
├── entangled.dhall
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
└── README.md
```

Create a home for your new project and push.

```sh
git add .
git commit -m 'initial commit'
git remote add origin git@github.com:joeplummer/my-awesome-project.git
git push -u origin main
```

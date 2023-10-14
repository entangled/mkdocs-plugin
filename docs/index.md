# Welcome to MkDocs Entangled Plugin
Using this plugin, you can make your Entangled documents look better.

## Examples
Detailed examples are found in the [entangled/mkdocs-examples repository](https://entangled.github.io/mkdocs-examples).

## Install

Install this with `pip install mkdocs-entangled-plugin`. To use the entangled plugin, add the following lines to your `mkdocs.yml`:

```yaml
plugins:
  - entangled  # this also runs `entangled sync` as a pre-build action

markdown_extensions:
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true 
```

Also create `entangled.toml`, the `version` field is obligatory.

```toml
version = "2.0"
watch_list = ["docs/**/*.md"]
hooks = ["build"]
```

## Components
This plugin bundles functionality for literate programming with Entangled.

- Annotate code blocks with titles.

### Annotate code blocks
The default markdown syntax that Entangled supports has fenced code blocks as follows

~~~markdown
``` {.python file=examples/hello_world.py}
if __name__ == "__main__":
    <<hello-world>>
```
~~~

Which renders like this:

``` {.python file=examples/hello_world.py}
if __name__ == "__main__":
    <<hello-world>>
```

Or named code blocks

~~~markdown
``` {.python #hello-world}
print("Hello, World!")
```
~~~

that render like this:

``` {.python #hello-world}
print("Hello, World!")
```

## License
Licensed under the Apache-2 license agreement: see LICENSE

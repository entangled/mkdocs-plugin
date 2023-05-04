# Welcome to MkDocs Entangled Plugin
Using this plugin, you can make your Entangled documents look better.

## Install

Install this with `pip install mkdocs-entangled-plugin`. To use the entangled plugin, add the following lines to your `mkdocs.yml`:

```yaml
plugins:
  - entangled

markdown_extensions:
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true 
```

## Components
This plugin bundles functionality for literate programming with Entangled.

- Annotate code blocks with titles.
- Build artifacts using Make.

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

### Build Artifacts

Build artifacts by specifying a Makefile.

~~~markdown
=== "Figure 1"

    ![](fig/plot.svg)

=== "Makefile"

    ``` {.make .build-artifact}
    .RECIPEPREFIX = >
  
    docs/fig/plot.svg:
    > mkdir -p $(@D)
    > gnuplot -e "set term svg; plot sin(x)" > $@
    ```
~~~

=== "Figure 1"

    ![](fig/plot.svg)

=== "Makefile"

    ``` {.make .build-artifact}
    .RECIPEPREFIX = >
  
    docs/fig/plot.svg:
    > mkdir -p $(@D)
    > gnuplot -e "set term svg; plot sin(x)" > $@
    ```

## License
Licensed under the Apache-2 license agreement: see LICENSE

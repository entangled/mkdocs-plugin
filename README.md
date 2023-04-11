# Welcome to MkDocs Entangled Plugin
Using this plugin, you can make your Entangled documents look better.

## Install

Install this with `pip install mkdocs-entangled-plugin`. To use the entangled plugin, add the following lines to your `mkdocs.yml`:

```yaml
plugins:
  - entangled

markdown_extensions:
  - pymdownx.superfences
```

## Annotates codeblocks
The default markdown syntax that Entangled supports has fenced code blocks as follows

~~~markdown
 ``` {.python file=hello_world.py}
 if __name__ == "__main__":
     <<hello-world>>
 ```
~~~

Which renders like this:

``` {.python file=hello_world.py}
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

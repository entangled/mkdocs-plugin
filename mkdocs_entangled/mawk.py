"""
μAwk, a tiny awk-like interface in Python
"""

from typing import Callable, Optional
from functools import wraps, partial
import re


def match_filter(expr: str, handler: Callable[[re.Match], Optional[list[str]]], inp: str) -> list[str]:
    if m := re.match(expr, inp):
        result = handler(m)
        if result is None:
            return [inp]
        else:
            return result
    else:
        return [inp]


def on_match(expr: str):
    """Decorator for doing search-and-replace based on a given regex.
    
    The inner function should take as argument a `re.Match` object
    and return a list of strings. The resulting decorated function
    then becomes a function from string to list of strings.
    
    If the input doesn't match the given regex, the original string
    is returned.
    
    The inner function may still decide to do nothing by returning None.
    
    To erase the matched input return the empty list.
    """
    return lambda f: wraps(f)(partial(match_filter, expr, f))


Rule = Callable[[str], list[str]]


def run(rules: list[Rule], inp: str) -> str:
    """Takes a list of rules, being function from `str` to `list[str]`.
    The input string is split into lines, after which each line is fed
    through the list of rules. All the results are colected into a list
    of strings and then joined by newline.
    """
    lines = inp.splitlines()
    result = []
    for l in lines:
        for r in rules:
            result.extend(r(l))
    return "\n".join(result)

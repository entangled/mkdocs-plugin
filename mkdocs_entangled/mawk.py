"""
μAwk, a tiny awk-like interface in Python
"""

from typing import Callable, Optional
from functools import wraps, partial
import re


"""Global counter to sort filters by the order in which they appear
in a class."""
_filter_creation_order = 0


def match_filter(expr: str, handler: Callable[[re.Match], Optional[list[str]]], inp: str) -> Optional[list[str]]:
    if m := re.match(expr, inp):
        return handler(m)
    return None


def on_match(expr: str):
    """Decorator for doing search-and-replace based on a given regex.
    
    The inner function should take as argument a `re.Match` object
    and return a list of strings. The resulting decorated function
    then becomes a function from string to list of strings.
    
    If the input doesn't match the given regex, the original string
    is returned.
    
    The inner function may still decide to do nothing by returning None.
    
    To erase the matched input return the empty list.

    This decorator also works on class methods. It is then assumed that
    the method has signature `(self, m: re.Match)`.
    """
    def _decorator(f):
        global _filter_creation_order
        method = len(f.__qualname__.split('.')) > 1
        if method:
            @wraps(f)
            def _impl(self, inp):
                return match_filter(expr, partial(f, self), inp)
            _impl._is_rule = _filter_creation_order  # add tag to method
            _filter_creation_order += 1
            return _impl
        else:
            return wraps(f)(partial(match_filter, expr, f))
    return _decorator


def always(f):
    """Suppose you have a rule with `@on_match(r".*")`, then it is better
    not to run the regex machinery at all and just pass on the string.
    In that case it is better to use `@always`."""
    global _filter_creation_order
    method = len(f.__qualname__.split('.')) > 1
    if method:
        f._is_rule = _filter_creation_order  # add tag to method
        _filter_creation_order += 1
        return f
    else:
        return f


Rule = Callable[[str], list[str]]


def run(rules: list[Rule], inp: str, exclusive=True) -> str:
    """Takes a list of rules, being function from `str` to `list[str]`.
    The input string is split into lines, after which each line is fed
    through the list of rules. All the results are colected into a list
    of strings and then joined by newline.
    """
    lines = inp.splitlines()
    result = []
    for l in lines:
        for r in rules:
            v = r(l)
            if v is not None:
                result.extend(v)
                if exclusive:
                    break
        else:
            result.append(l)
    return "\n".join(result)


class RuleSet:
    """To be used as a base class for classes that contain `on_match`
    decorated methods."""
    def list_rules(self):
        members = (getattr(self, m) for m in dir(self) if m[0] != '_')
        rules = [m for m in members if hasattr(m, '_is_rule')]
        return sorted(rules, key=lambda r: r._is_rule)

    def run(self, inp: str, exclusive=True) -> str:
        """Runs all rules in the class on input."""
        return run(self.list_rules(), inp, exclusive)

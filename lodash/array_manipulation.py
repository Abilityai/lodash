import re
from colorist import BrightColor
from typing import Callable, TypeVar, Any
from .string_manipulation import truncate_string

def get_element(a: list[Any], i: int) -> Any:
    return a[i % len(a)]


def fetch_element(my_list: dict | list, index, default_value=None):
    try:
        return my_list[index]
    except IndexError:
        return default_value


def colorized_arguments_to_string(*args, **kwds):
    """
    Convert the given arguments into a string representation with ASCII colorizing.

    Parameters:
        *args: Any number of positional arguments.
        **kwds: Any number of keyword arguments.

    Returns:
        str: The string representation of the arguments.
    """
    args_str = f"{BrightColor.BLACK},{BrightColor.OFF} ".join(repr(arg) for arg in args)
    kwds_str = f"{BrightColor.BLACK},{BrightColor.OFF} ".join(f"{BrightColor.BLACK}{key}={BrightColor.OFF}{BrightColor.WHITE}{repr(value)}{BrightColor.OFF}" for key, value in kwds.items())

    to_join = [args_str, kwds_str]
    to_join = [str for str in to_join if str]
    return ", ".join(to_join)


def arguments_to_string(*args, **kwds):
    """
    Convert the given arguments into a string representation.

    Parameters:
        *args: Any number of positional arguments.
        **kwds: Any number of keyword arguments.

    Returns:
        str: The string representation of the arguments.
    """
    args_str = ", ".join(repr(arg) for arg in args)
    kwds_str = ", ".join(f"{key}={repr(value)}" for key, value in kwds.items())

    to_join = [args_str, kwds_str]
    to_join = [str for str in to_join if str]
    return ", ".join(to_join)

def flatten(a: list[Any], level: int | None = None) -> list[Any]:
    result = []

    def _flatten_recursive(lst, curr_level):
        nonlocal level
        for item in lst:
            if isinstance(item, list):
                if level is None or curr_level < level:
                    _flatten_recursive(item, curr_level + 1)
                else:
                    result.append(item)
            else:
                result.append(item)

    _flatten_recursive(a, 0)
    return result


def compact(a):
    """
    Returns a new list with all the non-None elements from the input list.

    Args:
        a (list): The input list.

    Returns:
        list: A new list with all the non-None elements from the input list.
    """
    return [item for item in a if item is not None]

def compact_blank(a: list[str | None]) -> list[str]:
    return [item for item in a if item is not None and item.strip() != '']



T = TypeVar('T')
def uniq(a: list[T], l: Callable[[T, T], bool] = lambda x, y: x == y) -> list[T]:
    """
    Returns a new list containing only the unique elements from the input list `a`.

    Parameters:
    - `a` (list[T]): The input list from which to extract the unique elements.
    - `l` (Callable[[T, T], bool]): A function that compares two elements of
          type T and returns True if they are equal, and False otherwise.
          By default, it uses the `==` operator for comparison.

    Returns:
    - list[T]: A new list containing only the unique elements from the input list `a`.
    """
    result = []
    for elem in a:
        if not any(l(elem, existing) for existing in result):
            result.append(elem)
    return result

def wrap(a) -> list:
    if a is None:
        return []

    if isinstance(a, list):
        return a[:]

    if isinstance(a, tuple):
        return list(a)

    return [a]


def split_options(head: list, rest: list=[]) -> tuple[list, dict]:
    """
    Split a list into two parts based on options.

    Args:
        head (list): The list to be split.
        rest (list, optional): The initial value for the second part of the split list. Defaults to an empty list.

    Returns:
        tuple: A tuple containing two lists. The first list is the remaining items from the split, and the second list is the options extracted from the split.

    Raises:
        ValueError: If an invalid option is encountered in the input list.
    """
    if len(head) > 0 and not head[0].startswith('-'):
        return split_options(head[1:], rest + head[:1])
    else:
        opts = {}

        i = 0
        while i < len(head):
            if head[i].startswith('-') and not head[i+1].startswith('-'):
                key = re.sub('^-+', '', head[i])
                opts[key] = head[i+1]
                i += 2
            elif head[i].startswith('-') and '=' in head[i]:
                key, value = head[i].split('=')
                key = re.sub('^-+', '', key)
                opts[key] = value
                i += 1
            else:
                raise ValueError(f"Invalid option: {head[i]}")

        return rest, opts

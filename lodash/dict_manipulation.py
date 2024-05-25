import re
from copy import deepcopy

def _to_path(path):
    if isinstance(path, int):
        return [path]
    if isinstance(path, list):
        return path

    pattern = re.compile(r'[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["\'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))')
    parts = []
    def add_match(match):
        number, quote, subString = match.groups()
        if quote:
            parts.append(subString.replace(r'\\', '\\'))
        elif number:
            try:
                num = int(number)
                parts.append(num)
            except ValueError:
                parts.append(number)
        else:
            parts.append(match.group(0))


    re.sub(pattern, add_match, path)
    return parts


def dig(dictionary, *keys):
    def _get(d, k):
        if isinstance(d, (list, tuple)):
            if not isinstance(k, int):
                return None
            if k >= len(d):
                return None
            return d[k]
        elif isinstance(d, dict):
            return d.get(k)
        else:
            ValueError(f"Cannot get {k} from {d}")

    if not keys:
        return dictionary

    if len(keys) == 1:
        paths = _to_path(keys[0])

        if len(paths) == 1:
            return _get(dictionary, paths[0])
        else:
            return dig(dictionary, *paths)

    return dig(_get(dictionary, keys[0]), *keys[1:])


def digwrite(dictionary, key, value):
    dictionary = deepcopy(dictionary)
    paths = _to_path(key)

    def _set(d, path, val):
        if len(path) == 1:
            if isinstance(d, list) and isinstance(path[0], int):
                if path[0] < len(d):
                    d[path[0]] = val
                else:
                    d.append(val)
            elif isinstance(d, dict):
                d[path[0]] = val
            else:
                raise ValueError(f"Cannot set value at path {path} on {type(d)}")
        else:
            key = path[0]
            if isinstance(d, list) and isinstance(key, int):
                while key >= len(d):
                    d.append({})
                _set(d[key], path[1:], val)
            elif isinstance(d, dict):
                if key not in d:
                    d[key] = {}
                _set(d[key], path[1:], val)
            else:
                raise ValueError(f"Cannot navigate path {path} on {type(d)}")

    _set(dictionary, paths, value)
    return dictionary


if __name__ == '__main__':
    d = {
        'a': {
            'b': {
                'c': 1
            },
            'd': 2
        },
        'e': [
            {
                'f': 3,
                'g': []
            },
            4
        ]
    }

    def assertion(m, *args, result):
        v = m(d, *args)
        assert v == result, f"Expected: {result} for {args}, got: {repr(v)}"

    assertion(dig, 'a.b.c', result=1)
    assertion(dig, 'a.d', result=2)
    assertion(dig, 'e[0]', result={ 'f': 3, 'g': []})
    assertion(dig, 'e[0].f', result=3)
    assertion(dig, 'e[12].f', result=None)
    assertion(dig, 'e.0.f', result=None)
    assertion(dig, 'e.1', result=None)
    assertion(dig, 'e[1]', result=4)
    assertion(dig, 'a.b.d', result=None)
    assertion(dig, 'a.b.c.d', result=None)
    assertion(dig, ['a', 'b', 'c'], result=1)


    assertion(digwrite, 'a.b.c', 4, result={
        'a': {
            'b': {
                'c': 4
            },
            'd': 2
        },
        'e': [
            {
                'f': 3,
                'g': []
            },
            4
        ]
    })
    assertion(digwrite, 'e[0].f', 4, result={
        'a': {
            'b': {
                'c': 1
            },
            'd': 2
        },
        'e': [
            {
                'f': 4,
                'g': []
            },
            4
        ]
    })
    assertion(digwrite, 'a.b.d', 11, result={
        'a': {
            'b': {
                'c': 1,
                'd': 11
            },
            'd': 2
        },
        'e': [
            {
                'f': 3,
                'g': []
            },
            4
        ]
    })

    assertion(digwrite, 'e[0].g[0]', 'some_text', result={
        'a': {
            'b': {
                'c': 1
            },
            'd': 2
        },
        'e': [
            {
                'f': 3,
                'g': ['some_text']
            },
            4
        ]
    })

    print("Assertions passed")

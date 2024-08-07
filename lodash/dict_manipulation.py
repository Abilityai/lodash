import json
import re

import json5
from copy import deepcopy
from lodash.string_manipulation import truncate_string as truncate

def __int(v):
    try:
        return int(v)
    except ValueError:
        return 0

def __isint(v):
    return isinstance(v, int) or str(__int(v)) == str(v)

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

def _to_path_json_schema(path):
    paths = _to_path(path)
    result_paths = []
    for item in paths:
        if isinstance(item, str):
            result_paths.append('properties')
            result_paths.append(item)
        if isinstance(item, int):
            result_paths.append('items')

    return result_paths

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


def dig_json_schema(dictionary, key):
    paths = _to_path_json_schema(key)
    return dig(dictionary, *paths)


def digwrite(dictionary, key, value):
    dictionary = deepcopy(dictionary)
    paths = _to_path(key)

    def _set(d, path, val):
        if len(path) == 1:
            key = path[0]

            if key == '':
                if isinstance(d, list):
                    d.append(val)
                elif isinstance(d, dict):
                    raise ValueError(f"Cannot set value at path {path} on {type(d)}")
            elif isinstance(key, str) and len(key) > 0:
                if isinstance(d, list):
                    el = {}
                    d.append(el)
                    el[key] = val
                elif isinstance(d, dict):
                    d[key] = val
            elif isinstance(key, int):
                if isinstance(d, list):
                    if key >= len(d):
                        d.append(val)
                    else:
                        d[key] = val
                else:
                    raise ValueError(f"Cannot set value at path {path} on {type(d)}")
            else:
                raise ValueError(f"Cannot set value at path {path} on {type(d)}")
        else:
            key = path[0]
            key1 = path[1]
            rest = path[1:]

            if key == '':
                if key1 == '' or __isint(key1):
                    el = []
                    d.append(el)
                    _set(el, rest, val)
                elif isinstance(key1, str) and len(key1) > 0:
                    el = {}
                    d.append(el)
                    _set(el, rest, val)
                else:
                    raise ValueError(f"Cannot navigate path {path} on {type(d)}")
            elif isinstance(key, str) and len(key) > 0:
                if isinstance(d, list):
                    el = {}
                    d.append(el)
                    el[key] = {}
                    _set(el[key], rest, val)
                elif isinstance(d, dict):
                    if key not in d:
                        if key1 == '' or __isint(key1):
                            d[key] = []
                        elif isinstance(key1, str) and len(key1) > 0:
                            d[key] = {}
                        else:
                            raise ValueError(f"Cannot navigate path {path} on {type(d)}")
                    _set(d[key], rest, val)
                else:
                    raise ValueError(f"Cannot navigate path {path} on {type(d)}")
            elif isinstance(key, int):
                if isinstance(d, list):
                    if key >= len(d):
                        d.append({})
                    _set(d[key], rest, val)
                elif isinstance(d, dict):
                    _set(d[key], rest, val)
                else:
                    raise ValueError(f"Cannot navigate path {path} on {type(d)}")
            else:
                raise ValueError(f"Cannot navigate path {path} on {type(d)}")
    _set(dictionary, paths, value)
    return dictionary

def to_path(path: str) -> list[str | int]:
    """Converts a path-like string into a list of individual elements. Used by the `dig` and `digwrite` functions."""
    return _to_path(path)

def cut_up_values(data, max_length: int = 120, symbols='...'):
    def _cut_up_object(obj):
        if isinstance(obj, str):
            return truncate(obj, max_length=max_length, symbols=symbols, position='brackets')
        elif isinstance(obj, list):
            return [_cut_up_object(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: _cut_up_object(v) for k, v in obj.items()}
        elif isinstance(obj, tuple):
            return tuple(_cut_up_object(v) for v in obj)
        elif isinstance(obj, set):
            return {_cut_up_object(v) for v in obj}
        else:
            return obj

    return _cut_up_object(data)

def _add_index_comments(json_data):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            json_data[key] = add_index_comments(value)
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            comment = f' // index: {i}'
            item = add_index_comments(item)

            json_data[i] = f'{json5.dumps(item)}{comment}'
    return json_data


def add_index_comments(json_data):
    json_data = deepcopy(json_data)
    return _add_index_comments(json_data)

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

    assert to_path("a[0].b[3].c") == ['a', 0, 'b', 3, 'c']
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

    assertion(digwrite, 'e[].k[]', 'other_text', result={
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
            4,
            {
                'k': ['other_text']
            }
        ]
    })

    assertion(digwrite, 'e[0].k[].r', 'unexpected_raccoon', result={
        'a': {
            'b': {
                'c': 1
            },
            'd': 2
        },
        'e': [
            {
                'f': 3,
                'g': [],
                'k': [
                    {
                        'r': 'unexpected_raccoon'
                    }
                ]
            },
            4
        ]
    })

    assertion(digwrite, 'e[][][].r', 'unexpected_raccoon', result={
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
            4,
            [
                [
                    { 'r': 'unexpected_raccoon' }
                ]
            ]
        ]
    })
    from pathlib import Path
    with open(Path(__file__).parent / 'test_data' / 'schema.json', 'r') as f:
        json_schema = json.load(f)
        res = dig_json_schema(json_schema, "targetAudiences[1].generalDescription")
        assert res == json_schema["properties"]["targetAudiences"]["items"]["properties"]["generalDescription"]

        res = dig_json_schema(json_schema, "targetAudiences[3].profiles[2].jtbd")
        assert res == json_schema["properties"]["targetAudiences"]["items"]["properties"]["profiles"]["items"]["properties"]["jtbd"]

        res = dig_json_schema(json_schema, "targetAudiences[3].profiles[2].valueProposition.header")
        assert res == \
               json_schema["properties"]["targetAudiences"]["items"]["properties"]["profiles"]["items"]["properties"][
                   "valueProposition"]["properties"]["header"]

        res = dig_json_schema(json_schema, "targetAudiences[3].generalDescription.keyInterests")
        assert res == json_schema["properties"]["targetAudiences"]["items"]["properties"]["generalDescription"]["properties"]["keyInterests"]

        res = dig_json_schema(json_schema, "targetAudiences[3].generalDescription.audienceOverview")
        assert res == json_schema["properties"]["targetAudiences"]["items"]["properties"]["generalDescription"]["properties"]["audienceOverview"]

        res = dig_json_schema(json_schema, "product")
        assert res == json_schema["properties"]["product"]

        res = dig_json_schema(json_schema, "product.description")
        assert res == json_schema["properties"]["product"]["properties"]["description"]

        res = dig_json_schema(json_schema, "targetAudiences[3]")
        assert res == json_schema["properties"]["targetAudiences"]["items"]

        res = dig_json_schema(json_schema, "targetAudiences")
        assert res == json_schema["properties"]["targetAudiences"]

    print("Assertions passed")

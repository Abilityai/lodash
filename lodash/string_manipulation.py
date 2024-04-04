import re
import textwrap

def snake_to_camel(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))

def camel_to_snake(name: str) -> str:
    return re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', name).lower()

def snake_to_human(word: str) -> str:
    return ' '.join(x.capitalize() for x in word.split('_'))

def truncate_string(s, max_length=100, symbols='...'):
    if not isinstance(s, str):
        return s

    return (s[:max_length-3] + symbols) if len(s) > max_length else s

def indent(text, padding='    '):
    return '\n'.join(padding + line for line in text.split('\n'))

if __name__ == '__main__':
    def assertion(method, str1, str2):
        res = method(str1)
        assert res == str2, f"String split incortly input: {repr(str1)}, got: {repr(res)}, expected: {repr(str2)}"

    assertion(snake_to_camel, "lorem_ipsumlorem_ipsum", "LoremIpsumloremIpsum")
    assertion(snake_to_camel, "abcabc_xabcabc", "AbcabcXabcabc")
    assertion(snake_to_camel, "blah_blah_blah", "BlahBlahBlah")

    assertion(camel_to_snake, "AbcabcXabcabc", "abcabc_xabcabc")
    assertion(camel_to_snake, "AsdWerSdf", "asd_wer_sdf")
    assertion(camel_to_snake, "BlahBlahBlah", "blah_blah_blah")
    print("Assertions passed")
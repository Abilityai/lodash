import re
import textwrap
from typing import Literal

def snake_to_camel(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))

def camel_to_snake(name: str) -> str:
    return re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', name).lower()

def snake_to_human(word: str) -> str:
    return ' '.join(x.capitalize() for x in word.split('_'))

def truncate_string(s, max_length=100, symbols='...'):
    return (s[:max_length-3] + symbols) if len(s) > max_length else s


def truncate_string(s, max_length=100, symbols='...', position: Literal['start', 'end', 'brackets'] = 'end'):
    if not isinstance(s, str):
        return s

    if len(s) <= max_length:
        return s

    if position == 'start':
        return (symbols + s[-(max_length - len(symbols)):])

    if position == 'end':
        return (s[:max_length - len(symbols)] + symbols)

    if position == 'brackets':
        cut: int = int(max_length/2)
        if len(s) <= max_length*2:
            return s
        else:
            return s[:cut] + f'({symbols}{len(s[cut:-cut])}symbols{symbols})' + s[-cut:]

    raise ValueError(f"Invalid position for truncation {position}")


def dedent(text: str, multiline: bool=False):
    result = textwrap.dedent(text)
    if not multiline:
        chunk_results = []
        chunks = result.split(f"\n\n")
        for chunk in chunks:
            chunk_results.append(re.sub(r'\n', ' ', chunk))

        result = '\n'.join(chunk_results)
    return result.strip('\n').strip()


def indent(text, padding='    '):
    return '\n'.join(padding + line for line in text.split('\n'))


def convert_links_in_text_to_html(text):
    # This pattern matches URLs starting with http:// or https://
    url_pattern = r'(https?://[^\s]+)'
    html_text = re.sub(url_pattern, r'<a href="\1">\1</a>', text)
    return html_text


def extract_domain(url: str) -> str | None:
    # Regular expression to extract the domain from a URL
    regex = r"https?://(www\.)?([^/]+)"
    match = re.search(regex, url)
    if match:
        return match.group(2)
    else:
        return None


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
    assertion(convert_links_in_text_to_html, "BlahBlahBlah", "BlahBlahBlah")
    assertion(
        convert_links_in_text_to_html,
        "Visit our homepage at https://www.example.com and our blog at http://www.blog.example.com for more info.",
        'Visit our homepage at <a href="https://www.example.com">https://www.example.com</a> and our blog at <a href="http://www.blog.example.com">http://www.blog.example.com</a> for more info.')
    assertion(extract_domain, "https://www.example.ua.com", "example.ua.com")
    print("Assertions passed")

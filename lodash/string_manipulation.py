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


def dedent(text: str, multiline: bool=False):
    result = textwrap.dedent(text)
    if not multiline:
        result = re.sub(r'\n', ' ', text)
        result = re.sub(r'\n\n', '\n', text)
    result = text.strip('\n')
    return result.strip()


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

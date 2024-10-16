import re
import textwrap
from types import FunctionType, LambdaType
from typing import Literal, Any


def snake_to_camel(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))

def camel_to_snake(name: str) -> str:
    return re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', name).lower()

def snake_to_human(word: str) -> str:
    return ' '.join(x.capitalize() for x in word.split('_'))

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

def remove_quotes(text: str) -> str:
    for _ in range(3):
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        elif text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        elif text.startswith('```') and text.endswith('```'):
            # Remove the triple backticks at the start and end
            lines = text[3:-3].split('\n')
            # If there's more than one line and the first line doesn't contain spaces
            # (likely a language specifier), remove the first line
            lines = lines[1:] if len(lines) > 1 and ' ' not in lines[0] else lines
            # Join the remaining lines back into a single string
            text = '\n'.join(lines)
        elif text.startswith('`') and text.endswith('`'):
            text = text[1:-1]
        else:
            break

    # Check if text ends with ```, but not started with
    # (likely comment from LLM from the start)
    if text.endswith('```') and '```' in text[1:-3]:
        match = re.search(r'```(?:[a-zA-Z]+)?\n(.*?)```', str(text), re.DOTALL)
        text = match.group(1).strip() if match else text
        # Check if text starts with ```, but not ended with
        # (likely comment from LLM at the end)
        if text.startswith('```') and '```' in text[3:-1]:
            match = re.search(r'```(?:[a-zA-Z]+)?\n(.*?)```', str(text), re.DOTALL)
            text = match.group(1).strip() if match else text

    return text.strip('\n')

def split_keypath(path: str):
    parts = path.split('.')
    subparts = []
    for p in parts:
        subparts.extend(re.findall(r'\[.*?\]|[^\[\]]+', p))
    return subparts


def match_keypath(template: str, specific: str) -> bool:
    template_parts = split_keypath(template)
    specific_parts = split_keypath(specific)

    if len(template_parts) == 0:
        return True

    if len(template_parts) > len(specific_parts):
        return False

    for t_part, s_part in zip(template_parts, specific_parts):
        if t_part.startswith('['):
            if not re.match(r'\[-?\d+\]$', s_part):
                return False
            continue
        if t_part != s_part:
            return False

    return True

if __name__ == '__main__':
    import inspect
    tests: list[str] = []

    def should(*args: Any):
        if len(args) == 1:
            f = args[0]
            expected = True
        else:
            expected, f = args

        res = f() if callable(f) else f
        is_correct = (res != False and res is not None) if expected is None else (res == expected)
        source = inspect.getsource(f).strip()
        match = re.match(r'(should|shouldnt)\([^)]*\blambda: (.*)\)', source)
        if is_correct:
            tests.append("\033[92m.\033[0m")  # Append green dot for success to tests
        else:
            if match:
                source = match.group(2)
            tests.append(f"\033[91mF\033[0m")

            print(f"Failed: \033[91m{source}\033[0m, Got: \033[94m{repr(res)}\033[0m, Exp: \033[93m{repr(expected)}\033[0m")

    def shouldnt(*args: Any):
        if len(args) == 1:
            func = args[0]
            expected = False
        else:
            expected, func = args
            expected = not expected

        should(expected, func)

    # Tests for snake_to_camel
    should("LoremIpsumloremIpsum", lambda: snake_to_camel("lorem_ipsumlorem_ipsum"))
    should("AbcabcXabcabc", lambda: snake_to_camel("abcabc_xabcabc"))
    should("BlahBlahBlah", lambda: snake_to_camel("blah_blah_blah"))

    # # Tests for camel_to_snake
    should("abcabc_xabcabc", lambda: camel_to_snake("AbcabcXabcabc"))
    should("asd_wer_sdf", lambda: camel_to_snake("AsdWerSdf"))
    should("blah_blah_blah", lambda: camel_to_snake("BlahBlahBlah"))

    # # Tests for convert_links_in_text_to_html
    should("BlahBlahBlah", lambda: convert_links_in_text_to_html("BlahBlahBlah"))
    should(
        'Visit our homepage at <a href="https://www.example.com">https://www.example.com</a> and our blog at <a href="http://www.blog.example.com">http://www.blog.example.com</a> for more info.',
        lambda: convert_links_in_text_to_html("Visit our homepage at https://www.example.com and our blog at http://www.blog.example.com for more info.")
    )

    # # Tests for extract_domain
    should("example.ua.com", lambda: extract_domain("https://www.example.ua.com"))

    # # Tests for remove_quotes
    should("Hello, World!", lambda: remove_quotes('"Hello, World!"'))
    should("Python is awesome", lambda: remove_quotes("'Python is awesome'"))
    should("This is a code block", lambda: remove_quotes("```This is a code block```"))
    should("inline code", lambda: remove_quotes("`inline code`"))
    should('Triple quoted string', lambda: remove_quotes('"""Triple quoted string"""'))
    should("No quotes here", lambda: remove_quotes("No quotes here"))
    should('print("Hello")', lambda: remove_quotes('```python\nprint("Hello")\n```'))

    # # Tests for split_keypath
    should(["foo", "bar", "[baz]"], lambda: split_keypath("foo.bar[baz]"))
    should(["list", "[i]", "[j]", "items"], lambda: split_keypath("list[i][j].items"))
    should(["simple"], lambda: split_keypath("simple"))
    should(["complex", "[j]", "more", "[i]", "[k]"], lambda: split_keypath("complex[j].more[i][k]"))
    should(["[i]"], lambda: split_keypath("[i]"))
    should(["nested", "[i]", "path", "[j]", "end"], lambda: split_keypath("nested[i].path[j].end"))
    should(["numbers", "[3]", "digits", "[2]"], lambda: split_keypath("numbers[3].digits[2]"))
    should(["foo123", "bar456", "[7]"], lambda: split_keypath("foo123.bar456[7]"))

    # # Tests for match_keypath
    should(lambda: match_keypath("", ""))
    should(lambda: match_keypath("", "bar"))
    should(lambda: match_keypath("", "bar[2]"))
    should(lambda: match_keypath("", "bar[2].list[3].barr"))
    should(lambda: match_keypath("list[i]", "list[2].item"))
    should(lambda: match_keypath("list[i]", "list[2]"))
    should(lambda: match_keypath("list[i].item", "list[2].item"))
    should(lambda: match_keypath("list[i].items[j]", "list[2].items[3]"))
    should(lambda: match_keypath("list.items[i]", "list.items[8]"))
    should(lambda: match_keypath("list.items[i]", "list.items[-1]"))
    should(lambda: match_keypath("list[i][j]", "list[2][3]"))
    should(lambda: match_keypath("list[i][j]", "list[-1][-1]"))
    should(lambda: match_keypath("target[i].audience[j]", "target[0].audience[1]"))
    should(lambda: match_keypath("target[i]", "target[0].audience[1]"))
    should(lambda: match_keypath("target[i]", "target[-1].audience[1]"))
    should(lambda: match_keypath("target[i]", "target[-1].audience[-100]"))
    shouldnt(lambda: match_keypath("foo", ""))
    shouldnt(lambda: match_keypath("foo[i]", ""))
    shouldnt(lambda: match_keypath("list.items[i]", "list.items[j]"))
    shouldnt(lambda: match_keypath("list[i].item", "list[2]"))
    shouldnt(lambda: match_keypath("competitors[i]", "list[2]"))
    shouldnt(lambda: match_keypath("list[i].items[j]", "list[2].items"))
    shouldnt(lambda: match_keypath("list[i]", "list.items"))
    shouldnt(lambda: match_keypath("list[i][j]", "list[2]"))

    print("".join(tests))
    if not any(test == "\033[91mF\033[0m" for test in tests):
        print("\033[92mAssertions passed\033[0m")
    else:
        print("\033[91mAssertions failed\033[0m")

def remove_duplication(text: str) -> str:
    """
    Find the shortest repeating pattern in the given text.

    Parameters:
        text (str): The input text to search for repeating patterns.

    Returns:
        str: The shortest repeating pattern found in the text.
    """

    if not isinstance(text, str):
        return text
    length = len(text)
    mid_idx = length // 2

    if length == 1:
        return text

    if length % 2 == 0 and text[:mid_idx] == text[mid_idx:]:
        return text[:mid_idx]
    elif length % 2 != 0 and text[:mid_idx] == text[mid_idx+1:]:
        return text[:mid_idx]

    return text


if __name__ == "__main__":
    def assertion(str1, str2):
        res = remove_duplication(str1)
        assert res == str2, f"String split incortly input: {repr(str1)}, got: {repr(res)}, expected: {repr(str2)}"

    assertion("lorem ipsumlorem ipsum", "lorem ipsum")
    assertion("abcabcXabcabc", "abcabc")
    assertion("a", "a")
    assertion("aa", "a")
    assertion("abc", "abc")
    assertion(f"abaX\nabaX", "abaX")
    print("Assertions passed")

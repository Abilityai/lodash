def dig(dictionary: dict, *keys):
    if not keys:
        return dictionary

    key = keys[0]
    if key in dictionary:
        return dig(dictionary[key], *keys[1:])
    else:
        return None

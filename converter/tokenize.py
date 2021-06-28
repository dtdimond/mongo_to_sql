JSON_TOKENS = [",", ":", "{", "}", "[", "]"]


def tokenize(string):
    """
    Decomposes a string representation of json into a list of json tokens
    Tokens include: {, }, [, ], :, ,, strings, bools, null, numerics
    :param string: String representation of json
    :return: List of tokens
    """
    tokens = []

    while string:
        bool_or_null_token, string = tokenize_bool_or_null(string)
        if bool_or_null_token != -1:
            tokens.append(bool_or_null_token)
            continue

        num_token, string = tokenize_number(string)
        if num_token is not None:
            tokens.append(num_token)
            continue

        if string[0].isspace():
            string = string[1:]
            continue
        elif string[0] in JSON_TOKENS:
            tokens.append(string[0])
            string = string[1:]
            continue

        # Do strings last because we aren't requiring quotes around them
        str_token, string = tokenize_string(string)
        if str_token is not None:
            tokens.append(str_token)
            continue

    return tokens


def tokenize_string(string: str):
    """
    Attempt to parse the first part of 'string' into a str until we hit a
    terminal char. Handles both quoted strings and non-quoted
    :param string: Input stream
    :return: Token, remainder of string
    """
    if not string:
        return None, string

    ret_val = ''
    is_quoted = string[0] in ["'", '"']
    if is_quoted:
        string = string[1:]  # remove leading "'"

    for char in string:
        if is_quoted and char in ["'", '"']:
            return ret_val, string[len(ret_val) + 1:]
        elif not is_quoted and char in [":", ","]:
            return ret_val, string[len(ret_val):]
        else:
            ret_val += char

    if not is_quoted:
        return ret_val, string[len(ret_val):]

    raise ValueError(f"Reached string end without closing quote: {string}")


def tokenize_number(string):
    """
    Attempt to interpret the 'string' as a number token
    :param string: Input stream
    :return: Token, remainder of string
    """

    # accumulate all chars that might represent a number into num
    num = ''
    for char in string:
        if char.isnumeric() or char in ["-", "."]:
            num += char
        else:
            break

    if not num:  # No number found
        return None, string

    # Convert to float or int
    return (float(num) if "." in num else int(num)), string[len(num):]


def tokenize_bool_or_null(string):
    """
    Attempt to interpret the 'string' as a bool or None token
    :param string: Input stream
    :return: Token, remainder of string
    """

    if string.startswith("true"):
        return True, string[len("true"):]
    elif string.startswith("false"):
        return False, string[len("false"):]
    elif string.startswith("null"):
        return None, string[len("null"):]
    else:
        return -1, string  # Use -1 as "failure" case


if __name__ == "__main__":
    pass

from converter.tokenize import tokenize


def parse_mongo(str_input: str):
    """
    Decomposes a mongoDB type query in the form of a string into
    the relevant parts of the collection, query, and projection
    Does not support other params beyond these.

    The json parsing of the args relies on a two-step process, borrowing
    from lexical analysis:
    1) Tokenize the args into a list of json items
    2) Iteratively/recursively construct the json objects

    :param str_input: str representation of a mongo query
    :return: collection, query, projection
    """

    db, collection, full_method = str_input.split(".")

    method, args = full_method.split("(")
    if method != "find":
        raise ValueError(f"Method {method} unsupported")

    # Tokenize the args
    args = args.rstrip(");")
    tokens = tokenize(args)

    # Parse the query from the args, followed by the projection
    # If args are empty, pass both back as empty dict
    query = {}
    if tokens:
        query, tokens = parse(tokens)

    projection = {}
    if tokens:  # Note, the args are comma-sep, so proceed from tokens[1:]
        projection, tokens = parse(tokens[1:])

    return collection, query, projection


def parse(tokens):
    """
    Recursively parses a list of json tokens into the appropriate python
    objects. There are two scenarios:
    1) We start with an open '{', so attempt to parse a dict object
    2) We start with an open '[', so attempt to parse a list object
    3) Otherwise, just return
    :param tokens: List of json tokens
    :return: pair of parsed object, any remaining tokens
    """
    t = tokens[0]

    if t == "{":
        return parse_dict(tokens[1:])
    elif t == "[":
        return parse_list(tokens[1:])
    else:
        return t, tokens[1:]


def parse_list(tokens):
    # TODO - make more recursive
    parsed_list = []

    t = tokens[0]
    if t == "]":  # Case of an empty list
        return parsed_list, tokens[1:]

    # Recursively parse each each comma-separated token until
    #   we either reach an end brace or run out of items (failure case)
    while tokens:
        list_item, tokens = parse(tokens)
        parsed_list.append(list_item)

        t = tokens[0]
        if t == "]":
            return parsed_list, tokens[1:]
        elif t != ",":
            raise ValueError(f"List is not comma separated")
        else:
            tokens = tokens[1:]

    raise ValueError("Expected end of list bracket")


def parse_dict(tokens):
    parsed_dict = {}

    t = tokens[0]
    if t == "}":  # Case of empty dict
        return parsed_dict, tokens[1:]

    while tokens:
        parsed_key = tokens[0]
        if type(parsed_key) is str:
            tokens = tokens[1:]
        else:
            raise ValueError(f"Dict keys need to be str: {parsed_key}")

        # Recursively parse out the value for the key
        if tokens[0] != ":":
            raise ValueError(f"Dicts must be ':' separated, got: {t}")
        parsed_value, tokens = parse(tokens[1:])
        parsed_dict[parsed_key] = parsed_value

        # Move on to next item, or finish if closed dict brace
        t = tokens[0]
        if t == "}":
            return parsed_dict, tokens[1:]
        elif t != ",":
            raise ValueError(f"Expected comma after pair in object, got: {t}")

        tokens = tokens[1:]

    raise ValueError(f"Dict did not have closing brace")


if __name__ == "__main__":
    pass

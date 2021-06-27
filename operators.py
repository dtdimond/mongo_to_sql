"""
Module responsible for translating mongoDB operations to SQL equivalent.
Operations stored in a dict for easily extending to new ops in the future
if desired.
"""

logical_ops = {
    "$or": ' OR ',
    "$and": ' AND ',
}

comparison_ops = {
    "$lt": '<',
    "$lte": '<=',
    "$gt": '>',
    "$gte": '>=',
    "$ne": '!=',
    "$eq": '='
}


def convert_operation(operator: str, field: str, val: any) -> str:
    """
    Translate a mongoDB operation to SQL
    :param operator: See comparison_ops/custom_ops for supported list
    :param field: field to operate on
    :param val: value to compare field to via operator
    :return: SQL equivalent to the mongoDB operation
    """
    if operator in custom_ops:
        return custom_ops[operator](field, val)
    elif operator in comparison_ops:
        val_str = f"'{val}'" if isinstance(val, str) else f"{val}"
        return f"{field} {comparison_ops[operator]} {val_str}"
    else:
        raise ValueError(f"Operator not supported: {operator} for {field} {val}")


def in_op(field: str, vals: list) -> str:
    # $in operation translation
    return _in_op(field, vals, do_in=True)


def not_in_op(field: str, vals: list) -> str:
    # $ni operation translation
    return _in_op(field, vals, do_in=False)


def _in_op(field: str, vals: list, do_in: bool) -> str:
    if not isinstance(vals, list):
        raise ValueError(f"$in operator expects a list, got {vals} instead.")

    for i, val in enumerate(vals):
        vals[i] = f"'{val}'" if isinstance(val, str) else str(val)

    in_str = ", ".join(vals)
    not_str = " IN " if do_in else " NOT IN "
    return f"{field}{not_str}({in_str})"


# Operations that require some more custom logic than a straight translation
custom_ops = {
    "$in": in_op,
    "$ni": not_in_op,
}



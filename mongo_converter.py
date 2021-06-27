from operators import logical_ops, convert_operation


class MongoConverter:
    def __init__(self, _collection):
        """
        MongoConverter - converts a mongoDB-type query to SQL
        :param _collection: collection (~table) to query on
        """
        self.collection = _collection

    def find(self, query: dict = None, projection: dict = None) -> str:
        """
        Returns the SQL equivalent for the mongoDB type query. Only
        the query and projection params are supported.
        See:
        https://docs.mongodb.com/manual/reference/method/db.collection.find/

        :param query: The conditions (WHERE clause)
        :param projection: The fields to select. Exlcusion not supported
            because we don't have enough information about the underlying data.
        :return: Equivalent SQL
        """

        # Simply parse the projection and query to construct the final sql
        #  The majority of the hard-work is done by build_where_clause
        select_stmt = self._build_select_stmt(projection)
        where_stmt = self._build_where_stmt(query)

        sql = f"SELECT {select_stmt} FROM {self.collection}"
        if where_stmt:
            sql = f"{sql} WHERE {where_stmt}"

        return f"{sql};"

    @staticmethod
    def _build_select_stmt(projection: dict) -> str:
        # Return the fields to select. Returns '*' if projection is None

        selects = []
        if projection is not None:
            for select, enabled in projection.items():
                if not enabled:
                    raise ValueError(f"Exclusion not supported: {projection}")
                selects.append(select)
        select_stmt = "*" if not selects else ", ".join(selects)
        return select_stmt

    @staticmethod
    def _build_where_stmt(query: dict) -> str:
        # Build up the where clause for each item in query

        wheres = []
        query = dict() if query is None else query

        # Since python 3.7, dicts retain their order so
        #  OrderedDict is not necessary here to maintain proper ordering
        for k, v in query.items():
            wheres.append(build_where_clause(k, v))

        return " AND ".join(wheres)


def build_where_clause(field: str, val: any, operator=None):
    """
    This is the main logic of the parser and it works by recursively parsing
    the key/value pairs if there are nested layers (e.g. the value is itself
    a dict). The recursive approach leads to fairly readable code and
    mimics how you would do the conversion by hand in my opinion.
    There are a few scenarios:
    1) field is a 'logical'
        ex: {'$and': [...]} -> field = $and
        convert_logical() deals with this scenario, recursively if needed
    2) Operator has been passed in, meaning we're at a "leaf" of the recursion
        ex: {"$gte", 10}  -> op = "$gte"
    3) val is a dict
        ex: {"some_f": {"$gte", 10}}  -> field = "some_f", val = {...}
        we need to recursively parse the items in the val dict, being sure
        to keep track of "some_f" as the field name

    :param field: 'field' to operate on.
    :param val: val to be applied to the field. list, dict, or str/int/float
    :param operator: Optional operator to apply
    :return: Fully parsed sql where clause
    """
    if field in logical_ops:
        return convert_logical(field, val)
    elif operator is not None:
        return convert_operation(operator, field, val)
    elif isinstance(val, (str, int, float)):
        # ex: {"field": "val"} -> Equivalent to $eq operation
        return convert_operation("$eq", field, val)
    elif isinstance(val, dict):
        # Nested query, recurse down further
        wheres = []
        for operator, nested_val in val.items():
            wheres.append(build_where_clause(field, nested_val, operator))
        return " AND ".join(wheres)
    else:
        raise ValueError(f"Bad input for {field}: {val}")


def convert_logical(logical_op: str, val: list) -> str:
    """
    Handles converting a logical operation to SQL, also leveraging
    a recursive approach if needed.
    :param logical_op: The logical operator. e.g. "$and"
    :param val: list of sub-clauses to join together
    :return: SQL representation
    """
    sub_clauses = []
    for query in val:
        for nested_field, nested_val in query.items():
            sub_clauses.append(build_where_clause(nested_field, nested_val))

    return f"({logical_ops[logical_op].join(sub_clauses)})"


if __name__ == "__main__":
    users = MongoConverter("users")
    print(users.find({"name": "julio"}))

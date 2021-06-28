from converter.parser import parse_mongo
import pytest


class TestParser:

    def test_parse_one_arg(self):
        mongo = "db.user.find({name:'julio'});"
        collection, query, projection = parse_mongo(mongo)
        assert collection == "user"
        assert query == {"name": "julio"}
        assert projection == {}

    def test_parse_query_and_projection(self):
        mongo = "db.some_table.find({_id: 23113}, {name: 1, age: 1})"
        collection, query, projection = parse_mongo(mongo)
        assert collection == "some_table"
        assert query == {"_id": 23113}
        assert projection == {"name": 1, "age": 1}

    def test_empty(self):
        mongo = "db.user.find()"
        collection, query, projection = parse_mongo(mongo)
        assert collection == "user"
        assert query == {}
        assert projection == {}

    def test_in_operator(self):
        mongo = "db.user.find({name: {$in: [Dan, 'julio']}})"
        collection, query, projection = parse_mongo(mongo)
        assert collection == "user"
        assert query == {"name": {"$in": ["Dan", "julio"]}}
        assert projection == {}

    def test_logical_and(self):
        mongo = "db.user.find({$and: [{age: 10}, {_id: {$in: [10, -1]}}]})"
        collection, query, projection = parse_mongo(mongo)
        assert collection == "user"
        assert query == {"$and": [{"age": 10}, {"_id": {"$in": [10, -1]}}]}
        assert projection == {}

    def test_many_nested_conditions_with_whitespace(self):
        mongo = ("""
            db.user.find( {
                name: "julio",
                $and: [
                    {"age": {"$gte": 21, "$lte": 30}},
                    {
                        "$or": [
                            {"location": {"$in": ["US", "AUS"]}},
                            {"_id": {"$ni": [1, 2]}}
                        ]
                    }
                ]
            }, {id: true}
        """)
        collection, query, projection = parse_mongo(mongo)
        assert collection == "user"
        assert query == {
            "name": "julio",
            "$and": [
                {"age": {"$gte": 21, "$lte": 30}},
                {
                    "$or": [
                        {"location": {"$in": ["US", "AUS"]}},
                        {"_id": {"$ni": [1, 2]}},
                    ]
                },
            ],
        }
        assert projection == {"id": 1}

    def test_bad_input(self):
        with pytest.raises(ValueError):
            mongo = "db.user.find({name,:'julio'});"
            parse_mongo(mongo)

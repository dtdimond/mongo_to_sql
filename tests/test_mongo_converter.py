from mongo_converter import MongoConverter
import pytest


@pytest.fixture()
def user():
    # avoid repeating this line for each test
    yield MongoConverter("user")


class TestMongoConverter:
    def test_simple_find(self, user):
        sql = user.find({"name": "julio"})
        assert sql == "SELECT * FROM user WHERE name = 'julio';"

    def test_other_collection(self):
        other = MongoConverter("other")
        sql = other.find({"name": "julio"})
        assert sql == "SELECT * FROM other WHERE name = 'julio';"

    def test_empty_find(self, user):
        sql = user.find()
        assert sql == "SELECT * FROM user;"

    def test_query_with_projection(self, user):
        sql = user.find({"_id": 23113}, {"name": 1, "age": 1})
        assert sql == "SELECT name, age FROM user WHERE _id = 23113;"

    def test_projection_exclusion_fails(self, user):
        with pytest.raises(ValueError):
            user.find({"_id": 23113}, {"name": 0, "age": 1})

    def test_gte(self, user):
        sql = user.find({"age": {"$gte": 21}}, {"name": 1, "_id": 1})
        assert sql == "SELECT name, _id FROM user WHERE age >= 21;"

    def test_in_operator(self, user):
        sql = user.find({"name": {"$in": ['Dan', 'julio']}})
        assert sql == "SELECT * FROM user WHERE name IN ('Dan', 'julio');"

    def test_logical_and(self, user):
        query = {"$and": [{"age": 10}, {"_id": {"$in": [10, -1]}}]}
        sql = user.find(query)
        assert sql == "SELECT * FROM user WHERE (age = 10 AND _id IN (10, -1));"

    def test_logical_or(self, user):
        query = {"$or": [{"age": 10}, {"_id": {"$in": [10, -1]}}]}
        sql = user.find(query)
        assert sql == "SELECT * FROM user WHERE (age = 10 OR _id IN (10, -1));"

    def test_multiple_fields_with_multiple_comparison_ops(self, user):
        query = {
            "age": {"$gte": 21, "$lte": 30, "$ne": 22.1},
            "occupation": {"$eq": "law", "$gt": 30},
        }
        sql = user.find(query)
        assert sql == (
            "SELECT * FROM user WHERE age >= 21 AND age <= 30 AND age != 22.1"
            " AND occupation = 'law' AND occupation > 30;"
        )

    def test_many_nested_conditions(self, user):
        query = {
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
        sql = user.find(query)
        assert sql == (
            "SELECT * FROM user WHERE name = 'julio' "
            "AND (age >= 21 AND age <= 30 "
            "AND (location IN ('US', 'AUS') OR _id NOT IN (1, 2)));"
        )

    def test_bad_input(self, user):
        with pytest.raises(ValueError):
            user.find({"_id": {"user": [1, 2]}})

    def test_bad_nested_and(self, user):
        # This SQL is nonsensical: "WHERE b (age >= 21 AND age <= 30)"
        with pytest.raises(ValueError):
            query = {"b": {"$and": [{"age": {"$gte": 21, "$lte": 30}}]}}
            user.find(query)

    def test_sql_injection_attack(self, user):
        # Note - we don't handle this attack as you can see,
        #   but I wanted to highlight that with a test
        sql = user.find({"name": "';DROP TABLE USERS;"})
        assert sql == "SELECT * FROM user WHERE name = '';DROP TABLE USERS;';"

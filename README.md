# Mongo To SQL

This is a simple project meant to showcase implementing a simple MongoDB -> SQL query parser. Thanks for reviewing!

## Description

The MongoConverter class exposes the find(query, projection) function for converting a query on the class's collection (table equivalent in SQL) to SQL. Only find is currently supported and only the operators listed in the operators.py dict.

## Getting Started

### Dependencies

* python 3.7+
* See requirements.txt

### Executing program

* Setup/activate venv virtual environment
* pip install -r requirements.txt
* pytest .
* ./mongo_convert.py


```
from converter.mongo_converter import MongoConverter
from converter.parser import parse_mongo

mongo = "db.users.find({name: 'julio'})"
collection, query, projection = parse_mongo(mongo)
users = MongoConverter(collection)
print(users.find(query, projection))


# -> "SELECT * FROM users WHERE name = 'julio';"

```

## Authors

Dan Dimond

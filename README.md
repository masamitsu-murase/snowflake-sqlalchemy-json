[![PyPI version](https://badge.fury.io/py/snowflake-sqlalchemy-json.svg)](https://badge.fury.io/py/snowflake-sqlalchemy-json)
[![build](https://github.com/masamitsu-murase/snowflake-sqlalchemy-json/actions/workflows/ci.yml/badge.svg)](https://github.com/masamitsu-murase/snowflake-sqlalchemy-json/actions/workflows/ci.yml)

# snowflake-sqlalchemy-json

This is a library to handle JSON data in [snowflake-sqlalchemy](https://pypi.org/project/snowflake-sqlalchemy/).

## Installation

```bash
$ pip install snowflake-sqlalchemy-json
```

## Usage

Note that the current version support SELECT of JSON columns, but it does not support INSERT or UPDATE of them.

This library supports access to elements in JSON columns.  
You can access JSON columns as follows:

1. Define a column as `JSON` type.  
   Though the actual column type is `VARIANT`, you have to use `JSON` instead.
1. You can refer to elements in the column like `dict`.  
   If `Book` has a JSON column, `json_data`, you can refer to an element in the column as `Book.json_data["key"]`.
1. You can also use [`func.flatten` function](https://docs.snowflake.com/en/sql-reference/functions/flatten.html) to flatten values in a JSON column.  
   Please refer to the following example.

```python
import snowflake_sqlalchemy_json
from sqlalchemy import Column, Integer, JSON, String, func, select
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy.sql import quoted_name

# You have to call this function to enable `func.flatten`.
snowflake_sqlalchemy_json.register_json_handler()

Base: DeclarativeMeta = declarative_base()


class Book(Base):
    __tablename__ = quoted_name("database_name.schema_name.books", False)
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    json_data = Column(JSON)


editors = func.flatten(Book.json_data["editors"]).lateral()
query = select(
    Book.title,
    editors.c.value["name"],
).select_from(Book).join(
    editors,
    True,
).where(
    editors.c.value["type"] == "chief",
).order_by(editors.c.value["name"].desc())
```

`query` in the above example generates the following SQL.

```sql
SELECT database_name.schema_name.books.title, GET(anon_2.value, 'name') AS anon_1
FROM database_name.schema_name.books JOIN LATERAL flatten(INPUT => (GET(database_name.schema_name.books.json_data, 'editors'))) AS anon_2 ON true
WHERE GET(anon_2.value, 'type') = 'chief' ORDER BY GET(anon_2.value, 'name') DESC
```

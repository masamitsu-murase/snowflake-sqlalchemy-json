[![PyPI version](https://badge.fury.io/py/snowflake-sqlalchemy-json.svg)](https://badge.fury.io/py/snowflake-sqlalchemy-json)
[![build](https://github.com/masamitsu-murase/snowflake-sqlalchemy-json/actions/workflows/ci.yml/badge.svg)](https://github.com/masamitsu-murase/snowflake-sqlalchemy-json/actions/workflows/ci.yml)

# snowflake-sqlalchemy-json

This is a library to handle JSON data in [snowflake-sqlalchemy](https://pypi.org/project/snowflake-sqlalchemy/).

## Installation

```bash
$ pip install snowflake-sqlalchemy-json
```

## Usage

```python
import snowflake_sqlalchemy_json
from snowflake.sqlalchemy import dialect
from sqlalchemy import Column, Integer, JSON, String, func, select
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy.sql import quoted_name
import textwrap
import unittest

snowflake_sqlalchemy_json.register_json_handler()  # You have to call this function to enable `func.flatten`.

Base: DeclarativeMeta = declarative_base()


class Book(Base):
    __tablename__ = quoted_name("prefix1.prefix2.book", False)
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    author_id = Column(Integer)
    json_data = Column(JSON)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    age = Column(Integer)


editors = func.flatten(Book.json_data["editors"]).lateral()
query = select(
    Book.title,
    Book.json_data["editors"],
    func.max(Book.json_data["editors"]),
    editors.c.value["name"],
).select_from(Book).join(
    editors,
    editors.c.value["type"] == "chief"
).order_by(editors.c.value["name"].desc())
```

The above example generates the following SQL.

```sql
SELECT prefix1.prefix2.book.title, GET(prefix1.prefix2.book.json_data, 'editors') AS anon_1, max(GET(prefix1.prefix2.book.json_data, 'editors')) AS max_1, GET(anon_3.value, 'name') AS anon_2 
FROM prefix1.prefix2.book JOIN LATERAL flatten(INPUT => (GET(prefix1.prefix2.book.json_data, 'editors'))) AS anon_3 ON GET(anon_3.value, 'type') = 'chief' ORDER BY GET(anon_3.value, 'name') DESC
```

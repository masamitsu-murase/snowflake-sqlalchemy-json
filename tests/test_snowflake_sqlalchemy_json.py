import snowflake_sqlalchemy_json
from snowflake.sqlalchemy import dialect
from sqlalchemy import Column, Integer, JSON, String, func, select
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy.sql import quoted_name
import textwrap
import unittest

snowflake_sqlalchemy_json.register_json_handler()

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


class SnowflakeSqlalchemyJsonTest(unittest.TestCase):
    def compile_statement(self, statement):
        option = {"literal_binds": True}
        sql = statement.compile(dialect=dialect(), compile_kwargs=option)
        return str(sql)

    def test_package_load(self):
        self.assertIsNotNone(snowflake_sqlalchemy_json)

    def test_flatten(self):
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
        sql = self.compile_statement(query)
        expected_sql = """\
        SELECT prefix1.prefix2.book.title, GET(prefix1.prefix2.book.json_data, 'editors') AS anon_1, max(GET(prefix1.prefix2.book.json_data, 'editors')) AS max_1, GET(anon_3.value, 'name') AS anon_2 
        FROM prefix1.prefix2.book JOIN LATERAL flatten(INPUT => (GET(prefix1.prefix2.book.json_data, %(json_data_1)s))) AS anon_3 ON GET(anon_3.value, 'type') = 'chief' ORDER BY GET(anon_3.value, 'name') DESC
        """
        self.assertEqual(sql, textwrap.dedent(expected_sql).rstrip())

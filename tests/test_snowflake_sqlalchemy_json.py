import snowflake_sqlalchemy_json
import unittest


class SnowflakeSqlalchemyJsonTest(unittest.TestCase):
    def test_package_load(self):
        self.assertIsNotNone(snowflake_sqlalchemy_json)

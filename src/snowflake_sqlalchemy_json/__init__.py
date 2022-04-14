from snowflake.sqlalchemy.base import SnowflakeCompiler as SC
from sqlalchemy import INTEGER, JSON, column, func


def visit_json_flatten_func(self, fn, **kwargs):
    return "flatten(INPUT => %(expr)s)" % {"expr": self.function_argspec(fn)}


def visit_json_getitem_op_binary(self, binary, operator, **kw):
    return "GET(%s, %s)" % (self.process(binary.left, **
                                         kw), self.process(binary.right, **kw))


def json_flatten(value):
    return func.json_flatten(value).table_valued(
        column("INDEX", type_=INTEGER), column("VALUE", type_=JSON))


def register():
    functions = [
        visit_json_flatten_func,
        visit_json_getitem_op_binary,
    ]
    for function in functions:
        name = function.__name__
        if not hasattr(SC, name):
            setattr(SC, name, function)

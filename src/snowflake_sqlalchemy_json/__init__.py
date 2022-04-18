from snowflake.sqlalchemy.base import SnowflakeCompiler as SC
from sqlalchemy import Column, INTEGER, JSON, column, func
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.functions import GenericFunction


class flatten(GenericFunction):
    type = sqltypes.TableValueType(
            Column("index", type_=INTEGER), Column("value", type_=JSON)
        )

    def __init__(self, input_, *, path="", outer=False, recursive=False, mode='both'):
        super().__init__(input_)
        self._flatten_args = {
            "path": path,
            "outer": outer,
            "recursive": recursive,
            "mode": mode,
        }

    @property
    def flatten_args(self):
        return self._flatten_args


def visit_flatten_func(self, fn, **kwargs):
    flatten_expr = "flatten(INPUT => %s" % self.function_argspec(fn)
    flatten_args = fn.flatten_args
    flatten_expr += ", PATH => '" + flatten_args["path"] + "'"
    if flatten_args["outer"]:
        flatten_expr += ", OUTER => TRUE"
    else:
        flatten_expr += ", OUTER => FALSE"
    if flatten_args["recursive"]:
        flatten_expr += ", RECURSIVE => TRUE"
    else:
        flatten_expr += ", RECURSIVE => FALSE"
    flatten_expr += ", MODE => '" + flatten_args["mode"].upper() + "'"
    flatten_expr += ")"
    return flatten_expr


def visit_json_getitem_op_binary(self, binary, operator, **kw):
    return "GET(%s, %s)" % (self.process(binary.left, **
                                         kw), self.process(binary.right, **kw))


def json_flatten(value):
    return func.json_flatten(value).table_valued(
        column("INDEX", type_=INTEGER), column("VALUE", type_=JSON))


def register():
    functions = [
        visit_flatten_func,
        visit_json_getitem_op_binary,
    ]
    for function in functions:
        name = function.__name__
        if not hasattr(SC, name):
            setattr(SC, name, function)


register()

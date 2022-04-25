from snowflake.sqlalchemy.base import SnowflakeCompiler as SC
from snowflake.sqlalchemy.snowdialect import SnowflakeDialect as SD
from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.functions import GenericFunction
from typing import Optional

__all__ = ["register_json_handler"]


class flatten(GenericFunction):
    type = sqltypes.TableValueType(Column("seq", type_=Integer),
                                   Column("key", type_=String),
                                   Column("path", type_=String),
                                   Column("index", type_=Integer),
                                   Column("value", type_=JSON),
                                   Column("this", type_=JSON))
    MODE_LIST = ["OBJECT", "ARRAY", "BOTH"]

    def __init__(self,
                 input_,
                 *,
                 path: Optional[str] = None,
                 outer: Optional[bool] = None,
                 recursive: Optional[bool] = None,
                 mode: Optional[str] = None):
        super().__init__(input_)
        if mode is not None:
            mode = mode.upper()
            if mode not in flatten.MODE_LIST:
                raise ValueError(f"Unknown mode: '{mode}'")
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

    path = flatten_args["path"]
    if path is not None:
        flatten_expr += ", PATH => %s" % self.render_literal_value(
            path, sqltypes.STRINGTYPE)

    outer = flatten_args["outer"]
    if outer is not None:
        if outer:
            flatten_expr += ", OUTER => TRUE"
        else:
            flatten_expr += ", OUTER => FALSE"

    recursive = flatten_args["recursive"]
    if recursive is not None:
        if recursive:
            flatten_expr += ", RECURSIVE => TRUE"
        else:
            flatten_expr += ", RECURSIVE => FALSE"

    mode = flatten_args["mode"]
    if mode is not None:
        flatten_expr += ", MODE => %s" % self.render_literal_value(
            mode, sqltypes.STRINGTYPE)

    flatten_expr += ")"
    return flatten_expr


def visit_json_getitem_op_binary(self, binary, operator, **kw):
    expr = (self.process(binary.left, **kw), self.process(binary.right, **kw))
    return "GET(%s, %s)" % expr


def register_json_handler(include_snowflake_sqlalchemy_patch=True):
    functions = [
        visit_flatten_func,
        visit_json_getitem_op_binary,
    ]
    for function in functions:
        name = function.__name__
        if not hasattr(SC, name):
            setattr(SC, name, function)

    for json_converter in ["_json_serializer", "_json_deserializer"]:
        if not hasattr(SD, json_converter):
            setattr(SD, json_converter, None)

    if include_snowflake_sqlalchemy_patch:
        if "supports_statement_cache" not in SD.__dict__:
            setattr(SD, "supports_statement_cache", False)

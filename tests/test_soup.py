from typing import List, Optional

import pytest
from bs4 import BeautifulSoup
from tests.fixtures import HTML

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.soup import get_attr
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList


class SoupSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    # Soup
    lang: ScField[str, SoupFind("<html>", callback=get_attr("lang"))]
    charset: ScField[
        str,
        SoupFind(
            "<meta>", callback=get_attr("charset"), factory=lambda s: s.replace("-", "")
        ),
    ]
    title: ScField[str, SoupFind({"name": "title"})]
    title_lower: ScField[
        str, SoupSelect("head > title", factory=lambda text: text.lower())
    ]
    body_string: ScField[str, SoupFind('<p class="body-string>')]
    body_string_chars: ScField[
        List[str], SoupFind('<p class="body-string>', factory=list)
    ]
    body_string_flag: ScField[bool, SoupSelect("body > p.body-string")]
    body_int: ScField[int, SoupFind('<p class="body-int">')]
    body_float: ScField[float, SoupSelect("body > p.body-int")]
    body_int_x10: ScField[
        int, SoupSelect("body > p.body-int", factory=lambda el: int(el) * 10)
    ]

    fail_value_1: ScField[Optional[str], SoupFind({"name": "spam"})]
    fail_value_2: ScField[bool, SoupFind("<spam>")]
    fail_value_3: ScField[str, SoupSelect("body > spam.egg", default="spam")]

    # SoupList
    body_int_list: ScField[List[int], SoupFindList('<a class="body-list">')]
    body_float_list: ScField[List[float], SoupSelectList("body > a.body-list")]
    max_body_list: ScField[
        int,
        SoupFindList(
            {"name": "a", "class_": "body-list"},
            factory=lambda els: max(int(i) for i in els),
        ),
    ]
    body_float_flag: ScField[
        bool, SoupFindList({"name": "a", "class_": "body-list"}, factory=bool)
    ]

    fail_list_1: ScField[Optional[List[int]], SoupFindList({"name": "spam"})]
    fail_list_2: ScField[bool, SoupSelectList("body > spam.egg")]
    fail_list_3: ScField[
        List[str], SoupFindList('<spam class="egg">', default=["spam", "egg"])
    ]


SOUP_SCHEMA = SoupSchema(HTML)


@pytest.mark.parametrize(
    "attr,result",
    [
        ("lang", "en"),
        ("charset", "UTF8"),
        ("title", "TEST PAGE"),
        ("title_lower", "test page"),
        ("body_string", "test-string"),
        ("body_string_chars", ["t", "e", "s", "t", "-", "s", "t", "r", "i", "n", "g"]),
        ("body_string_flag", True),
        ("body_int", 555),
        ("body_float", 555.0),
        ("body_int_x10", 5550),
        ("fail_value_1", None),
        ("fail_value_2", False),
        ("fail_value_3", "spam"),
        ("body_int_list", [666, 777, 888]),
        ("body_float_list", [666.0, 777.0, 888.0]),
        ("max_body_list", 888),
        ("body_float_flag", True),
        ("fail_list_1", None),
        ("fail_list_2", False),
        ("fail_list_3", ["spam", "egg"]),
    ],
)
def test_soup_parse(attr, result):
    value = getattr(SOUP_SCHEMA, attr)
    assert value == result

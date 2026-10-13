import pytest

from pipeline.budget_summary import _num, norm_label
from pipeline.checks import check_tree
from pipeline.ontario import _clean_label
from pipeline.ontario import _num as ont_num


def test_num_parses_brackets_as_negative():
    assert _num("(1,234)") == -1234
    assert _num("5.4%") == 5.4
    assert _num("n/a") is None


def test_norm_label_unifies_dashes_and_case():
    assert norm_label("Toronto Transit Commission – Wheel-Trans") == "toronto transit commission wheel trans"


def test_ontario_label_strips_footnotes():
    assert _clean_label("Long-Term Care (Total)5") == "Long-Term Care (Total)"
    assert _clean_label("Interest and Other Debt Servicing Charges7") == "Interest and Other Debt Servicing Charges"
    assert _clean_label("Health (Total)") == "Health (Total)"


def test_ontario_num_dash_is_zero():
    assert ont_num("–") == 0
    assert ont_num("(1.1)") == -1.1


@pytest.mark.parametrize("child_sum,ok", [(10.0, True), (10.4, True), (11.0, False)])
def test_check_tree_tolerance(child_sum, ok):
    errors = []
    tree = {"name": "root", "gross": 10.0, "children": [{"name": "a", "gross": child_sum - 4}, {"name": "b", "gross": 4}]}
    check_tree(tree, "root", errors)
    assert (not errors) == ok


def test_check_tree_rejects_unknown_category():
    errors = []
    check_tree({"name": "x", "gross": 1, "category": "spaceships"}, "x", errors)
    assert errors

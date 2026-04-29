import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


def _mock_conn(rows, columns):
    cur = MagicMock()
    cur.fetchall.return_value = rows
    cur.description = [(col,) for col in columns]
    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn


@patch("db._connect")
def test_query_returns_dataframe(mock_connect):
    import db
    mock_connect.return_value = _mock_conn([(1, "foo")], ["ID", "NAME"])
    result = db._query("SELECT 1")
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["ID", "NAME"]
    assert len(result) == 1


@patch("db._connect")
def test_get_headline_metrics_columns(mock_connect):
    import db
    mock_connect.return_value = _mock_conn(
        [("2025-01-01", 10000.0, 100, 500)],
        ["MONTH", "TOTAL_REVENUE", "TOTAL_ORDERS", "TOTAL_ITEMS"],
    )
    result = db.get_headline_metrics.__wrapped__()
    assert set(result.columns) == {"MONTH", "TOTAL_REVENUE", "TOTAL_ORDERS", "TOTAL_ITEMS"}


@patch("db._connect")
def test_get_bundle_pairs_columns(mock_connect):
    import db
    mock_connect.return_value = _mock_conn(
        [("Widget A", "Widget B", 42)],
        ["PRODUCT_A", "PRODUCT_B", "CO_PURCHASE_COUNT"],
    )
    result = db.get_bundle_pairs.__wrapped__()
    assert "CO_PURCHASE_COUNT" in result.columns
    assert result.iloc[0]["CO_PURCHASE_COUNT"] == 42


@patch("db._connect")
def test_get_refund_rates_columns(mock_connect):
    import db
    mock_connect.return_value = _mock_conn(
        [("Widget A", 200, 10, 5.0)],
        ["PRODUCT_NAME", "TOTAL_ORDERS", "REFUND_COUNT", "REFUND_RATE_PCT"],
    )
    result = db.get_refund_rates.__wrapped__()
    assert "REFUND_RATE_PCT" in result.columns


@patch("db._connect")
def test_get_new_vs_returning_columns(mock_connect):
    import db
    mock_connect.return_value = _mock_conn(
        [("New", "Widget A", 5000.0), ("Returning", "Widget B", 8000.0)],
        ["CUSTOMER_TYPE", "PRODUCT_NAME", "REVENUE"],
    )
    result = db.get_new_vs_returning.__wrapped__()
    assert set(result.columns) == {"CUSTOMER_TYPE", "PRODUCT_NAME", "REVENUE"}
    assert set(result["CUSTOMER_TYPE"].unique()) == {"New", "Returning"}

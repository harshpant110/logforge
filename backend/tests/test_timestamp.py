from datetime import datetime, timezone

import pytest

from app.mapper.ocsf_mapper import convert_timestamp


def test_iso_timestamp():

    result = convert_timestamp(
        "2026-09-06T12:00:00Z"
    )

    expected = int(
        datetime(
            2026,
            9,
            6,
            12,
            0,
            0,
            tzinfo=timezone.utc,
        ).timestamp() * 1000
    )

    assert result == expected


def test_syslog_timestamp():

    result = convert_timestamp(
        "Sep 6 12:00:01",
        syslog_year=2026,
        syslog_timezone="UTC",
    )

    expected = int(
        datetime(
            2026,
            9,
            6,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ).timestamp() * 1000
    )

    assert result == expected


def test_missing_timestamp():

    result = convert_timestamp(None)

    assert isinstance(result, int)
    assert result > 0


def test_invalid_timestamp():

    with pytest.raises(
        ValueError,
        match="Invalid timestamp format",
    ):
        convert_timestamp("not-a-real-timestamp")
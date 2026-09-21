
from datetime import datetime, timedelta, timezone

from app.services.sla_service import SLAService


def test_calculate_due_at_for_urgent_priority():
    created_at = datetime(
        2026,
        9,
        21,
        10,
        0,
        tzinfo=timezone.utc,
    )

    due_at = SLAService.calculate_due_at(
        priority="urgent",
        created_at=created_at,
    )

    assert due_at == created_at + timedelta(hours=4)


def test_calculate_due_at_for_high_priority():
    created_at = datetime(
        2026,
        9,
        21,
        10,
        0,
        tzinfo=timezone.utc,
    )

    due_at = SLAService.calculate_due_at(
        priority="high",
        created_at=created_at,
    )

    assert due_at == created_at + timedelta(hours=24)


def test_calculate_due_at_for_medium_priority():
    created_at = datetime(
        2026,
        9,
        21,
        10,
        0,
        tzinfo=timezone.utc,
    )

    due_at = SLAService.calculate_due_at(
        priority="medium",
        created_at=created_at,
    )

    assert due_at == created_at + timedelta(hours=48)


def test_calculate_due_at_for_low_priority():
    created_at = datetime(
        2026,
        9,
        21,
        10,
        0,
        tzinfo=timezone.utc,
    )

    due_at = SLAService.calculate_due_at(
        priority="low",
        created_at=created_at,
    )

    assert due_at == created_at + timedelta(hours=72)


def test_sla_is_breached():
    current_time = datetime(
        2026,
        9,
        21,
        12,
        0,
        tzinfo=timezone.utc,
    )

    due_at = datetime(
        2026,
        9,
        21,
        10,
        0,
        tzinfo=timezone.utc,
    )

    assert SLAService.is_breached(
        sla_due_at=due_at,
        current_time=current_time,
    ) is True


def test_sla_is_not_breached():
    current_time = datetime(
        2026,
        9,
        21,
        8,
        0,
        tzinfo=timezone.utc,
    )

    due_at = datetime(
        2026,
        9,
        21,
        10,
        0,
        tzinfo=timezone.utc,
    )

    assert SLAService.is_breached(
        sla_due_at=due_at,
        current_time=current_time,
    ) is False


def test_sla_without_due_date_is_not_breached():
    assert SLAService.is_breached(
        sla_due_at=None,
    ) is False
    
    
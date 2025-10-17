"""
Timezone-aware datetime utilities.

All timestamps in the application should use the configured timezone
from the app_settings table, not the server's timezone.
"""
from datetime import datetime
from typing import Optional
import pytz
import logging

logger = logging.getLogger(__name__)

_cached_timezone: Optional[str] = None


def get_configured_timezone() -> str:
    """
    Get the configured timezone from database settings.

    Returns:
        Timezone string (e.g., 'America/Puerto_Rico')
        Defaults to 'America/Puerto_Rico' (AST) if not configured
    """
    global _cached_timezone

    # Return cached value if available
    if _cached_timezone:
        return _cached_timezone

    try:
        from database_models import AppSettings
        from database import Database

        db = Database()
        with db.session() as session:
            setting = session.query(AppSettings).filter_by(setting_key='timezone').first()
            if setting:
                _cached_timezone = setting.setting_value
                return _cached_timezone

    except Exception as e:
        logger.warning(f"Failed to load timezone from database: {e}")

    # Default to AST
    default_tz = 'America/Puerto_Rico'
    logger.info(f"Using default timezone: {default_tz}")
    return default_tz


def clear_timezone_cache():
    """Clear the cached timezone value. Call this when timezone setting changes."""
    global _cached_timezone
    _cached_timezone = None
    logger.info("Timezone cache cleared")


def now_in_timezone() -> datetime:
    """
    Get current datetime in the configured timezone.

    Returns:
        Timezone-aware datetime object in configured timezone
    """
    tz_name = get_configured_timezone()
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)


def get_timezone_aware_datetime(dt: datetime) -> datetime:
    """
    Convert a naive datetime to timezone-aware datetime in configured timezone.

    Args:
        dt: Naive datetime object

    Returns:
        Timezone-aware datetime in configured timezone
    """
    tz_name = get_configured_timezone()
    tz = pytz.timezone(tz_name)

    if dt.tzinfo is None:
        # Naive datetime - localize it
        return tz.localize(dt)
    else:
        # Already timezone-aware - convert to configured timezone
        return dt.astimezone(tz)


def format_datetime(dt: datetime, format_type: str = 'full') -> str:
    """
    Format datetime for display in configured timezone.

    Args:
        dt: Datetime object (naive or aware)
        format_type: 'full', 'date', 'time', 'short', 'relative'

    Returns:
        Formatted datetime string
    """
    # Convert to timezone-aware
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    tz_dt = get_timezone_aware_datetime(dt) if dt.tzinfo is None else dt.astimezone(pytz.timezone(get_configured_timezone()))

    if format_type == 'full':
        # "October 17, 2025 11:30 AM AST"
        return tz_dt.strftime('%B %d, %Y %I:%M %p %Z')
    elif format_type == 'date':
        # "Oct 17, 2025"
        return tz_dt.strftime('%b %d, %Y')
    elif format_type == 'time':
        # "11:30 AM"
        return tz_dt.strftime('%I:%M %p')
    elif format_type == 'short':
        # "Oct 17, 11:30 AM"
        return tz_dt.strftime('%b %d, %I:%M %p')
    elif format_type == 'relative':
        # "Today, 11:30 AM" or "Yesterday, 11:30 AM" or "Oct 17"
        now = now_in_timezone()
        delta = now.date() - tz_dt.date()

        if delta.days == 0:
            return f"Today, {tz_dt.strftime('%I:%M %p')}"
        elif delta.days == 1:
            return f"Yesterday, {tz_dt.strftime('%I:%M %p')}"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            return tz_dt.strftime('%b %d, %Y')
    else:
        return tz_dt.isoformat()


def to_iso_string(dt: Optional[datetime] = None) -> str:
    """
    Convert datetime to ISO string in configured timezone.

    Args:
        dt: Datetime object (uses now if None)

    Returns:
        ISO format string
    """
    if dt is None:
        dt = now_in_timezone()
    elif dt.tzinfo is None:
        dt = get_timezone_aware_datetime(dt)

    return dt.isoformat()

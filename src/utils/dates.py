from datetime import date, datetime, timedelta


def previous_week_range(issue_date: date | None = None):
    if issue_date is None:
        issue_date = date.today()
    weekday = issue_date.weekday()
    monday_this_week = issue_date - timedelta(days=weekday)
    start = monday_this_week - timedelta(days=7)
    end = monday_this_week - timedelta(days=1)
    return start, end


def get_last_week_range(issue_date: date | None = None):
    if issue_date is None:
        issue_date = date.today()
    start, end = previous_week_range(issue_date)
    return start, end, issue_date.isoformat()


def iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")

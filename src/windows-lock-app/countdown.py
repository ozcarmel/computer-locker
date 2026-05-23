def format_seconds(total_seconds):
    """Format a non-negative duration as MM:SS."""
    seconds = max(0, int(total_seconds))
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def next_remaining_seconds(started_at, duration_seconds, now):
    elapsed = max(0, int(now - started_at))
    return max(0, int(duration_seconds) - elapsed)

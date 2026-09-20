HISTORY_LIMIT = 5
_history = []


def add_entry(operation_str, result):
    """Add a calculation record to history."""
    if len(_history) >= HISTORY_LIMIT:
        _history.pop(0)
    _history.append((operation_str, result))


def get_history(limit=None):
    """Return the last 'limit' history entries."""
    if limit is None or limit > len(_history):
        limit = len(_history)
    return _history[-limit:]

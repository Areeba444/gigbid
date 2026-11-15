def should_promote_style_edit(edit_count: int, consistent_pattern: bool) -> bool:
    """Explicit promotion rule: user edit patterns require at least 2 consistent edits
    or explicit user confirmation before being promoted into durable style memory.
    Raw agent outputs and unverified edits are strictly rejected.
    """
    return edit_count >= 2 and consistent_pattern

def should_promote_outcome(status: str, connects_spent: int) -> bool:
    """Promote outcomes when a verifiable response (replied, hired, or confirmed ignored)
    is recorded by the marketplace port.
    """
    return status in ["replied", "hired", "ignored"]

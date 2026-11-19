"""Check temporal evidence for a single grant and commit, without re-grants."""

from graphlib import CycleError, TopologicalSorter


def check_authorization_order(events, precedence, *, grant, commit, withdrawals):
    """Return an ordering verdict and compatible witness orders.

    The caller independently binds receipt IDs to the same subject, grant and
    effect. Precedence pairs are witnessed causal edges. Withdrawals is the
    complete inventory of effective withdrawals, or None when scope is open.
    The verdict concerns timing within that supplied evidence.
    """
    if isinstance(events, str) or isinstance(withdrawals, str):
        raise ValueError("pass collections of event IDs")
    events = tuple(events)
    if any(type(event) is not str or not event for event in events):
        raise ValueError("event IDs must be nonempty strings")
    known = set(events)
    if len(known) != len(events):
        raise ValueError("duplicate event ID")
    related = (grant, commit, *(() if withdrawals is None else withdrawals))
    if any(type(event) is not str or event not in known for event in related):
        raise ValueError("unknown grant, commit or withdrawal")
    if len(set(related)) != len(related):
        raise ValueError("grant, commit and withdrawals must be distinct")
    edges = tuple(precedence)
    for edge in edges:
        if not isinstance(edge, (tuple, list)) or len(edge) != 2:
            raise ValueError("precedence edges must be pairs")
        before, after = edge
        if any(type(event) is not str or event not in known for event in edge):
            raise ValueError("invalid precedence edge")
        if before == after:
            raise ValueError("invalid precedence edge")

    def ordered(extra):
        sorter = TopologicalSorter({event: () for event in events})
        for before, after in (*edges, *extra):
            sorter.add(after, before)
        try:
            return tuple(sorter.static_order())
        except CycleError:
            return None

    if ordered(()) is None:
        raise ValueError("causal evidence contains a cycle")
    if withdrawals is None:
        return {"verdict": "incomplete_scope", "supporting_order": None, "opposing_order": None}

    required = ((grant, commit), *((commit, event) for event in related[2:]))
    supporting = ordered(required)
    opposing = None
    for before, after in required:
        opposing = ordered(((after, before),))
        if opposing is not None:
            break

    if supporting is None:
        verdict = "excluded"
    elif opposing is None:
        verdict = "forced"
    else:
        verdict = "ambiguous"
    return {"verdict": verdict, "supporting_order": supporting, "opposing_order": opposing}

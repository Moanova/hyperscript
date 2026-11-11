# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : participation_badge_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Pure logic for the participation badge of block nodes (TSK08, FN030/SU008).

Kept free of any Qt dependency so it can be unit tested without a
QApplication. The BlockNode visual items consume these helpers.

Behavior kept from planoscript (adopted session 03): fixed-size badge with the
participation count, hidden at 0, '9+' beyond 9, and an 'Agents:' line in the
tooltip (at most 3 names, then '+n more').
"""


class ParticipationBadgeService:
    """Pure helpers for the participation badge of a block node."""

    BADGE_MAX_DISPLAY_COUNT = 9
    TOOLTIP_MAX_NAMES = 3

    @classmethod
    def badge_text(cls, count: int) -> str:
        """Return the text displayed in the badge for a given count.

        '9+' beyond 9 (the badge stays a fixed size regardless of the
        number of participants, for readability).
        """
        if count > cls.BADGE_MAX_DISPLAY_COUNT:
            return f"{cls.BADGE_MAX_DISPLAY_COUNT}+"
        return str(count)

    @classmethod
    def badge_visible(cls, count: int) -> bool:
        """The badge is hidden when no agent participates in the block."""
        return count > 0

    @classmethod
    def tooltip_agents_line(cls, agent_labels) -> str:
        """Return the 'Agents:' tooltip line for a list of agent labels.

        Lists at most TOOLTIP_MAX_NAMES names, then '+n more'.
        Returns an empty string for an empty list.
        """
        labels = [str(lb) for lb in agent_labels if lb]
        if not labels:
            return ""
        shown = labels[:cls.TOOLTIP_MAX_NAMES]
        line = "Agents: " + ", ".join(shown)
        remaining = len(labels) - len(shown)
        if remaining > 0:
            line += f" +{remaining} more"
        return line

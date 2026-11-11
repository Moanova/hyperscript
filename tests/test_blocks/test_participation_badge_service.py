# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_participation_badge_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for ParticipationBadgeService (TSK08) - badge behavior kept
from planoscript: hidden at 0, '9+' beyond 9, 'Agents:' tooltip line."""

from core.services.participation_badge_service import ParticipationBadgeService


def test_badge_hidden_at_zero():
    assert ParticipationBadgeService.badge_visible(0) is False
    assert ParticipationBadgeService.badge_visible(1) is True
    assert ParticipationBadgeService.badge_visible(12) is True


def test_badge_text_caps_at_9_plus():
    assert ParticipationBadgeService.badge_text(1) == "1"
    assert ParticipationBadgeService.badge_text(9) == "9"
    assert ParticipationBadgeService.badge_text(10) == "9+"
    assert ParticipationBadgeService.badge_text(42) == "9+"


def test_tooltip_agents_line():
    assert ParticipationBadgeService.tooltip_agents_line([]) == ""
    assert ParticipationBadgeService.tooltip_agents_line(["Hero"]) == "Agents: Hero"
    assert ParticipationBadgeService.tooltip_agents_line(["A", "B", "C"]) == "Agents: A, B, C"
    assert ParticipationBadgeService.tooltip_agents_line(["A", "B", "C", "D", "E"]) == "Agents: A, B, C +2 more"

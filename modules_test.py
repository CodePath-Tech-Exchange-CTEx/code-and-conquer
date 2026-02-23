# test_modules.py
"""
Pytest smoke tests for modules.py UI helpers.

These tests monkeypatch Streamlit functions so they run headless in CI/local.
They verify:
 - sample_groups() returns expected sample data
 - primary display functions run without raising exceptions
 - Join/Leave buttons toggle st.session_state as expected
"""

import pytest
import streamlit as st

# Import the module under test. Adjust if your module path differs.
import modules as mod


# -------------------------
# Fixtures / helpers
# -------------------------
class DummyCtx:
    """A no-op context manager used to simulate st.container / column contexts."""
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

    # allow calls like ctx.subelement() to be no-ops
    def __call__(self, *a, **k):
        return None


@pytest.fixture(autouse=True)
def patch_streamlit(monkeypatch):
    """
    Monkeypatch Streamlit functions used by modules.py to avoid real UI.

    - Replace basic writers with no-ops.
    - Replace st.container, st.columns, st.expander with dummy contexts.
    - Replace st.image, st.info, st.success with no-ops.
    - Replace st.button with a controllable fake that returns True only when
      st._simulate_button_press_key matches the button key.
    - Ensure st.session_state is available as a dict.
    """
    # No-op output functions
    monkeypatch.setattr(st, "title", lambda *a, **k: None)
    monkeypatch.setattr(st, "write", lambda *a, **k: None)
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(st, "info", lambda *a, **k: None)
    monkeypatch.setattr(st, "success", lambda *a, **k: None)
    monkeypatch.setattr(st, "divider", lambda *a, **k: None)

    # image is a no-op that accepts args
    monkeypatch.setattr(st, "image", lambda *a, **k: None)

    # container / expander return context managers
    monkeypatch.setattr(st, "container", lambda *a, **k: DummyCtx())
    monkeypatch.setattr(st, "expander", lambda *a, **k: DummyCtx())

    # dynamic fake_columns: return N DummyCtx objects based on requested columns
    def fake_columns(*args, **kwargs):
        """
        Accept calls like st.columns(4) or st.columns([0.2, 0.8]) and return a
        list of DummyCtx of appropriate length.
        """
        if args:
            spec = args[0]
            # If spec is an int (newer style), use it
            if isinstance(spec, int):
                n = spec
            else:
                # if spec is a sequence/list of column widths, return that many
                try:
                    n = len(spec)
                except Exception:
                    n = 2
        else:
            # Default to 2 columns if nothing provided
            n = 2
        return [DummyCtx() for _ in range(n)]

    monkeypatch.setattr(st, "columns", fake_columns)

    # controllable fake button: returns True only when st._simulate_button_press_key matches key
    def fake_button(label=None, key=None, *a, **k):
        simulate = getattr(st, "_simulate_button_press_key", None)
        return key is not None and simulate == key
    monkeypatch.setattr(st, "button", fake_button)

    # Ensure session_state exists as a simple dict for observation
    if not hasattr(st, "session_state") or not isinstance(st.session_state, dict):
        monkeypatch.setattr(st, "session_state", {}, raising=False)

    yield

    # cleanup simulated key if present
    if hasattr(st, "_simulate_button_press_key"):
        delattr(st, "_simulate_button_press_key")


# -------------------------
# Tests
# -------------------------
def test_sample_groups_contents():
    """sample_groups should return a list of dicts and expected example titles."""
    groups = mod.sample_groups()
    assert isinstance(groups, list)
    assert len(groups) >= 1

    # check at least the first two groups and some expected fields/values
    titles = [g.get("title") for g in groups]
    assert "Advanced Chemistry" in titles
    assert "Astronomy" in titles

    # inspect one group's keys
    g0 = groups[0]
    for k in ("title", "schedule", "mode", "members", "group_chat_label", "is_member"):
        assert k in g0


def test_display_my_groups_page_runs():
    """display_my_groups_page should run without raising (uses sample data)."""
    groups = mod.sample_groups()
    # Should not raise
    mod.display_my_groups_page(groups, two_columns=True, mockup_image_path=None)


def test_group_card_join_sets_session_state():
    """
    Simulate pressing the Join button for card index 0 and verify session_state is set.
    """
    # Ensure clean session state
    st.session_state.clear()

    group = {
        "title": "Test Join Group",
        "schedule": "Wed",
        "mode": "Online",
        "members": "1/8 Members",
        "icon": None,
        "group_chat_label": "Group Chat",
        "is_member": False,
        "highlighted": False,
    }

    # Simulate pressing join button by setting the simulate key to join_0
    st._simulate_button_press_key = "join_0"

    # Call the card renderer (should set joined_0 True)
    mod.display_group_card(group, card_index=0)

    assert st.session_state.get("joined_0", False) is True

    delattr(st, "_simulate_button_press_key")


def test_group_card_leave_sets_session_state():
    """
    Pre-populate joined_1 True then simulate pressing Leave; expect False after.
    """
    st.session_state.clear()

    group = {
        "title": "Member Group",
        "is_member": True,
    }

    # Pre-initialize join state as the UI code would
    st.session_state["joined_1"] = True

    # Simulate pressing Leave
    st._simulate_button_press_key = "leave_1"
    mod.display_group_card(group, card_index=1)

    assert st.session_state.get("joined_1", None) is False

    delattr(st, "_simulate_button_press_key")


def test_display_post_and_genai_advice_and_custom_component_run():
    """Ensure post, genai advice, and custom component renderers run without exception."""
    # Minimal inputs
    mod.display_my_custom_component("Remi")
    mod.display_post(
        username="Remi",
        user_image=None,
        timestamp="2024-01-01 12:00",
        content="Test post content",
        post_image=None,
    )
    mod.display_genai_advice("2024-01-01 08:00", "Keep it up!", image=None)


def test_activity_and_recent_workouts_run():
    """Exercise activity summary and recent workouts using small sample data."""
    workouts = [
        {"workout_id": "w1", "start_timestamp": "2024-01-01 00:00:00", "distance": 3.2, "steps": 4000, "calories_burned": 150},
        {"workout_id": "w2", "start_timestamp": "2024-01-02 00:00:00", "distance": 2.5, "steps": 3000, "calories_burned": 120},
    ]
    # These should not raise
    mod.display_activity_summary(workouts)
    mod.display_recent_workouts(workouts)

# test_mygroups.py
"""
Pytest tests for modules_mygroups.py

These tests are intentionally lightweight:
- They monkeypatch commonly-used streamlit functions to no-op or predictable
  behaviors so tests run in CI / headless environments.
- They assert that the UI functions run without raising and that the "Join"
  button toggles the expected session_state key when simulated.
"""

import builtins
import types
import pytest

import streamlit as st

# Import the module under test. Adjust import path if you named it differently.
import modules_mygroups as mg


# ---------------------------
# Utilities / fixtures
# ---------------------------

class DummyCtx:
    """A simple no-op context manager for `st.container()` and column contexts."""
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def patch_streamlit(monkeypatch):
    """
    Monkeypatch commonly-used streamlit functions/objects so tests run headless.

    - st.title, st.write, st.markdown, st.subheader, st.image, st.info, st.success:
        replaced with no-op functions that record calls if needed.
    - st.columns and st.container return context managers (so "with st.columns(...):"
        works in the code).
    - st.button is replaced with a controllable fake that returns True only when
      st._simulate_button_press_key equals the button's key. This lets tests
      simulate pressing a specific button (e.g., "join_0").
    - st.session_state is ensured to be a dict to observe side-effects.
    """
    # replace simple writers with no-op functions
    monkeypatch.setattr(st, "title", lambda *a, **k: None)
    monkeypatch.setattr(st, "write", lambda *a, **k: None)
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(st, "image", lambda *a, **k: None)
    monkeypatch.setattr(st, "info", lambda *a, **k: None)
    monkeypatch.setattr(st, "success", lambda *a, **k: None)

    # Provide a container context manager
    monkeypatch.setattr(st, "container", lambda *a, **k: DummyCtx())

    # st.columns should return a list of DummyCtx objects with the requested length
    def fake_columns(spec):
        # if spec is a number (legacy style), produce that many contexts
        try:
            n = int(len(spec)) if hasattr(spec, "__len__") else 2
        except Exception:
            n = 2
        return [DummyCtx() for _ in range(2)]
    monkeypatch.setattr(st, "columns", lambda *a, **k: [DummyCtx(), DummyCtx()])

    # Replace st.button with controllable fake that returns True when the
    # button key matches st._simulate_button_press_key
    def fake_button(label=None, key=None, *a, **k):
        # If a test sets st._simulate_button_press_key to a key, that specific
        # button call will return True (simulate press). Otherwise False.
        simulate = getattr(st, "_simulate_button_press_key", None)
        return key is not None and simulate == key

    monkeypatch.setattr(st, "button", fake_button)

    # Ensure session_state exists and starts empty for each test
    if not hasattr(st, "session_state") or not isinstance(st.session_state, dict):
        monkeypatch.setattr(st, "session_state", {}, raising=False)

    yield
    # cleanup: remove any simulate key after test
    if hasattr(st, "_simulate_button_press_key"):
        delattr(st, "_simulate_button_press_key")


# ---------------------------
# Tests
# ---------------------------

def test_sample_groups_structure():
    """sample_groups() should return a list of dicts with expected keys."""
    groups = mg.sample_groups()
    assert isinstance(groups, list)
    assert len(groups) >= 1
    # Check expected keys exist on first entry
    first = groups[0]
    assert "title" in first
    assert "schedule" in first
    assert "mode" in first
    assert "members" in first


def test_display_my_groups_page_runs_without_error():
    """Calling display_my_groups_page should not raise when streamlit is patched."""
    groups = mg.sample_groups()
    # Should run without exceptions
    mg.display_my_groups_page(groups, two_columns=True, mockup_image_path=None)


def test_display_group_card_join_updates_session_state():
    """
    Simulate pressing the Join button for card index 0.
    After calling display_group_card, st.session_state['joined_0'] should be True.
    """
    # Ensure session state is clean
    st.session_state.clear()

    # Create a sample group that's not already a member
    group = {
        "title": "Test Group",
        "schedule": "Wed",
        "mode": "Online",
        "members": "1/8 Members",
        "icon": None,
        "group_chat_label": "Group Chat",
        "is_member": False,   # start as not a member
        "highlighted": False,
    }

    # Tell fake_button which button key to simulate pressing.
    # display_group_card uses keys: f"join_{card_index}" for the Join button.
    st._simulate_button_press_key = "join_0"

    # Call the function under test; because fake_button returns True for key 'join_0',
    # the function will set st.session_state["joined_0"] = True
    mg.display_group_card(group, card_index=0)

    # Assert join state was set
    assert st.session_state.get("joined_0", False) is True

    # Clean up the simulated key
    delattr(st, "_simulate_button_press_key")


def test_display_group_card_leave_updates_session_state():
    """
    Simulate pressing Leave when user is already a member.
    - Pre-populate st.session_state joined_1 = True
    - Simulate pressing 'leave_1' button and verify state becomes False
    """
    # Prepare group where user is a member
    st.session_state.clear()
    group = {
        "title": "Member Group",
        "is_member": True,
    }

    # Pre-initialize the join key as module code does if absent
    st.session_state["joined_1"] = True

    # Simulate pressing the Leave button
    st._simulate_button_press_key = "leave_1"
    mg.display_group_card(group, card_index=1)

    # After pressing leave, the module sets joined_1 = False
    assert st.session_state.get("joined_1", None) is False

    # cleanup
    delattr(st, "_simulate_button_press_key")

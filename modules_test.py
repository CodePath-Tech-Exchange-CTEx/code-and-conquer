# test_modules.py
"""
Pytest smoke tests for the simplified my-groups modules.
"""

import pytest
import streamlit as st
import modules as mod


class DummyCtx:
    """No-op context manager to simulate columns / containers / expanders."""
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def __call__(self, *a, **k):
        return None


@pytest.fixture(autouse=True)
def patch_streamlit(monkeypatch):
    # Replace rendering functions with no-ops
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "write", lambda *a, **k: None)
    monkeypatch.setattr(st, "title", lambda *a, **k: None)
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(st, "info", lambda *a, **k: None)
    monkeypatch.setattr(st, "success", lambda *a, **k: None)

    # image and container no-ops
    monkeypatch.setattr(st, "image", lambda *a, **k: None)
    monkeypatch.setattr(st, "container", lambda *a, **k: DummyCtx())
    monkeypatch.setattr(st, "expander", lambda *a, **k: DummyCtx())

    # dynamic columns implementation: return N DummyCtx items
    def fake_columns(spec=None, *a, **k):
        if isinstance(spec, int):
            n = spec
        else:
            try:
                n = len(spec)
            except Exception:
                n = 2
        return [DummyCtx() for _ in range(n)]
    monkeypatch.setattr(st, "columns", fake_columns)

    # button is controllable via st._simulate_button_press_key
    def fake_button(label=None, key=None, *a, **k):
        simulate = getattr(st, "_simulate_button_press_key", None)
        return key is not None and simulate == key
    monkeypatch.setattr(st, "button", fake_button)

    # ensure session_state dict
    if not hasattr(st, "session_state") or not isinstance(st.session_state, dict):
        monkeypatch.setattr(st, "session_state", {}, raising=False)

    yield

    # cleanup simulated key
    if hasattr(st, "_simulate_button_press_key"):
        delattr(st, "_simulate_button_press_key")


def test_sample_groups_structure():
    groups = mod.sample_groups()
    assert isinstance(groups, list)
    assert len(groups) == 3
    titles = [g["title"] for g in groups]
    assert "Advanced Chemistry" in titles
    assert "Biology" in titles


def test_display_my_groups_page_runs():
    groups = mod.sample_groups()
    mod.display_my_groups_page(groups, two_columns=True)


def test_join_button_sets_session_state():
    st.session_state.clear()
    group = {
        "title": "Test Group",
        "schedule": "Wed",
        "mode": "Online",
        "members": "1/8 Members",
        "is_member": False,
    }
    # simulate pressing join for index 0
    st._simulate_button_press_key = "join_0"
    mod.display_group_card(group, 0)
    assert st.session_state.get("joined_0", False) is True
    delattr(st, "_simulate_button_press_key")


def test_leave_button_sets_session_state():
    st.session_state.clear()
    group = {
        "title": "Member Group",
        "is_member": True,
    }
    st.session_state["joined_1"] = True
    st._simulate_button_press_key = "leave_1"
    mod.display_group_card(group, 1)
    assert st.session_state.get("joined_1", None) is False
    delattr(st, "_simulate_button_press_key")

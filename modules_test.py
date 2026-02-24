import unittest
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


class TestMyGroups(unittest.TestCase):
    """Tests for the My Groups page in modules.py (no GenAI tests)."""

    def setUp(self):
        # Save originals so we can restore after each test
        self._orig = {}

        for name in (
            "markdown", "write", "title", "caption", "subheader", "info", "success", "error",
            "image", "container", "expander", "columns", "button"
        ):
            self._orig[name] = getattr(st, name, None)

        # Replace rendering functions with no-ops
        st.markdown = lambda *a, **k: None
        st.write = lambda *a, **k: None
        st.title = lambda *a, **k: None
        st.caption = lambda *a, **k: None
        st.subheader = lambda *a, **k: None
        st.info = lambda *a, **k: None
        st.success = lambda *a, **k: None
        st.error = lambda *a, **k: None

        # image and container no-ops
        st.image = lambda *a, **k: None
        st.container = lambda *a, **k: DummyCtx()
        st.expander = lambda *a, **k: DummyCtx()

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
        st.columns = fake_columns

        # button is controllable via st._simulate_button_press_key
        def fake_button(label=None, key=None, *a, **k):
            simulate = getattr(st, "_simulate_button_press_key", None)
            return key is not None and simulate == key
        st.button = fake_button

        # ensure session_state dict
        if not hasattr(st, "session_state") or not isinstance(st.session_state, dict):
            st.session_state = {}

    def tearDown(self):
        # cleanup simulated key
        if hasattr(st, "_simulate_button_press_key"):
            try:
                delattr(st, "_simulate_button_press_key")
            except Exception:
                pass

        # restore originals
        for name, val in self._orig.items():
            if val is None:
                if hasattr(st, name):
                    try:
                        delattr(st, name)
                    except Exception:
                        pass
            else:
                setattr(st, name, val)

    def test_sample_groups_structure(self):
        groups = mod.sample_groups()
        self.assertIsInstance(groups, list)
        self.assertEqual(len(groups), 3)

        titles = [g["title"] for g in groups]
        self.assertIn("Advanced Chemistry", titles)
        self.assertIn("Biology", titles)

    def test_display_my_groups_page_runs(self):
        groups = mod.sample_groups()
        # should not raise
        mod.display_my_groups_page(groups, two_columns=True)

    def test_join_button_sets_session_state(self):
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

        self.assertIs(st.session_state.get("joined_0", False), True)

        # cleanup simulated key explicitly
        if hasattr(st, "_simulate_button_press_key"):
            delattr(st, "_simulate_button_press_key")

    def test_leave_button_sets_session_state(self):
        st.session_state.clear()

        group = {
            "title": "Member Group",
            "is_member": True,
        }

        st.session_state["joined_1"] = True

        # simulate pressing leave for index 1
        st._simulate_button_press_key = "leave_1"
        mod.display_group_card(group, 1)

        self.assertIs(st.session_state.get("joined_1", None), False)

        # cleanup simulated key explicitly
        if hasattr(st, "_simulate_button_press_key"):
            delattr(st, "_simulate_button_press_key")


if __name__ == "__main__":
    unittest.main()

# tests/test_modules.py
import importlib
import modules
import pytest

# --- Simple Streamlit stub used by tests ---
class StreamlitStub:
    def __init__(self, button_map=None):
        """
        button_map: dict mapping button key -> bool (True -> simulated click)
        """
        self.button_map = button_map or {}
        self.logs = []
import unittest
from streamlit.testing.v1 import AppTest
from modules import display_user_profile

    # container context manager
    class Ctx:
        def __init__(self, parent):
            self.parent = parent
        def __enter__(self):
            self.parent.logs.append(("enter_container", None))
            return self
        def __exit__(self, exc_type, exc, tb):
            self.parent.logs.append(("exit_container", None))

    def container(self):
        return StreamlitStub.Ctx(self)
APP_FILE = "app.py"


class TestDisplayUserProfile(unittest.TestCase):

    def test_profile_renders_without_exception(self):
        """Test that the profile page loads cleanly with no errors."""
        at = AppTest.from_file(APP_FILE).run()

        assert not at.exception

    def test_full_name_displayed(self):
        """Test that the user's full name appears as a subheader."""
        at = AppTest.from_file(APP_FILE).run()

        subheader_values = [s.value for s in at.subheader]
        assert any("Jane Doe" in v for v in subheader_values)

    def test_stats_display_correct_values(self):
        """Test that all three stat metrics show the correct values."""
        at = AppTest.from_file(APP_FILE).run()

        metric_labels = [m.label for m in at.metric]
        metric_values = [m.value for m in at.metric]
        assert metric_values[metric_labels.index("Groups Joined")] == "4"
        assert metric_values[metric_labels.index("Study Hours")] == "127"
        assert metric_values[metric_labels.index("Day Streak")] == "12"

    def test_availability_slots_displayed(self):
        """Test that time slot captions are rendered in the availability section."""
        at = AppTest.from_file(APP_FILE).run()

        caption_values = [c.value for c in at.caption]
        assert any("9-11 AM" in v for v in caption_values)
        assert any("1-3 PM" in v for v in caption_values)

    def test_focus_subjects_displayed(self):
        """Test that focus subjects appear on the page."""
        at = AppTest.from_file(APP_FILE).run()

        all_text = " ".join([str(m.value) for m in at.markdown])
        assert "Data Structures" in all_text
        assert "Machine Learning" in all_text

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    # column context manager with simple proxies
    class ColumnCtx:
        def __init__(self, parent, idx):
            self.parent = parent
            self.idx = idx
        def __enter__(self):
            self.parent.logs.append(("enter_column", self.idx))
            return self
        def __exit__(self, exc_type, exc, tb):
            self.parent.logs.append(("exit_column", self.idx))
        def markdown(self, txt, unsafe_allow_html=False):
            self.parent.logs.append(("markdown", txt))
        def write(self, txt):
            self.parent.logs.append(("write", txt))
        def button(self, label, key=None, use_container_width=None):
            self.parent.logs.append(("button_call", {"label": label, "key": key}))
            return self.parent.button_map.get(key, False)

    def columns(self, count_or_list, gap=None):
        if isinstance(count_or_list, (list, tuple)):
            n = len(count_or_list)
        else:
            n = int(count_or_list)
        return [StreamlitStub.ColumnCtx(self, i) for i in range(n)]

    # basic functions used by modules
    def markdown(self, txt, unsafe_allow_html=False):
        self.logs.append(("markdown", txt))
    def write(self, txt):
        self.logs.append(("write", txt))
    def button(self, label, key=None, use_container_width=None):
        self.logs.append(("button_call", {"label": label, "key": key}))
        return self.button_map.get(key, False)

    # helpers some code might call
    def info(self, txt):
        self.logs.append(("info", txt))
    def title(self, txt):
        self.logs.append(("title", txt))
    def text_input(self, label):
        self.logs.append(("text_input", label))
        return ""

# Helper to reload modules before each test for a clean state
def reload_modules():
    importlib.reload(modules)
    return modules

# -------------------------
# Tests (pytest functions)
# -------------------------

def test_group_card_without_click():
    """group_card should render texts and NOT call callback when button not clicked."""
    m = reload_modules()
    stub = StreamlitStub(button_map={})  # no clicks
    m.st = stub

    called = {"happened": False}
    def on_chat(group):
        called["happened"] = True

    group = {"name": "Test Group", "icon": "🧪", "days": "Tue", "mode": "Online", "members": "3/4 Members"}
    m.group_card(group, on_chat=on_chat, key_prefix="testg")

    assert called["happened"] is False

    # ensure name and metadata were written
    texts = " ".join(str(t) for typ, t in stub.logs if typ in ("write", "markdown"))
    assert "Test Group" in texts
    assert "Tue" in texts
    assert "Online" in texts
    assert "3/4 Members" in texts


def test_group_card_with_click():
    """group_card should call on_chat when Group Chat button clicked."""
    m = reload_modules()
    gname = "Clickable Group"
    key_prefix = "kp"
    chat_key = f"{key_prefix}_chat_{gname}"
    stub = StreamlitStub(button_map={chat_key: True})
    m.st = stub

    payload = {}
    def on_chat(group):
        payload["group"] = group

    group = {"name": gname, "icon": "🔭", "days": "Mon", "mode": "In person", "members": "2/5 Members"}
    m.group_card(group, on_chat=on_chat, key_prefix=key_prefix)

    assert "group" in payload
    assert payload["group"]["name"] == gname


def test_join_group_card_click():
    """join_group_card should call on_join when Browse Groups clicked."""
    m = reload_modules()
    stub = StreamlitStub(button_map={"join_test": True})
    m.st = stub

    called = {"join": False}
    def on_join():
        called["join"] = True

    m.join_group_card(label="Join Test", on_join=on_join, key="join_test")
    assert called["join"] is True

    written = " ".join(str(t) for typ, t in stub.logs if typ in ("write", "markdown"))
    assert "Join Test" in written


def test_render_my_groups_page_layout_and_join_button_key():
    """render_my_groups_page should lay out tiles and attempt join button key(s)."""
    m = reload_modules()
    stub = StreamlitStub(button_map={})
    m.st = stub

    groups = [
        {"name": "G1", "icon": "1", "days":"D1", "mode":"M1", "members":"1/3"},
        {"name": "G2", "icon": "2", "days":"D2", "mode":"M2", "members":"2/3"},
        {"name": "G3", "icon": "3", "days":"D3", "mode":"M3", "members":"3/3"},
    ]

    m.render_my_groups_page(groups, on_chat=None, on_join=None, columns=2)

    # extract button keys from logs
    button_calls = [entry for typ, entry in stub.logs if typ == "button_call"]
    keys = [call.get("key") for call in button_calls if isinstance(call, dict)]

    assert any(k is not None and str(k).startswith("join") for k in keys)

    written = " ".join(str(t) for typ, t in stub.logs if typ in ("write", "markdown"))
    assert "G1" in written
    assert "G2" in written
    assert "G3" in written

import streamlit as st

from backend.chat_handler import get_messages, get_new_messages, send_message


POLL_INTERVAL_SECONDS = 2


def _init_group_chat_state() -> None:
    if "chat_messages_by_group" not in st.session_state:
        st.session_state.chat_messages_by_group = {}
    if "chat_last_ts_by_group" not in st.session_state:
        st.session_state.chat_last_ts_by_group = {}
    if "chat_seen_ids_by_group" not in st.session_state:
        st.session_state.chat_seen_ids_by_group = {}


def _prime_cache(group_id: str) -> None:
    """Load the full message history once per session per group."""
    if group_id in st.session_state.chat_messages_by_group:
        return

    history = get_messages(group_id)
    st.session_state.chat_messages_by_group[group_id] = list(history)
    st.session_state.chat_seen_ids_by_group[group_id] = {
        m.get("id") for m in history if m.get("id") is not None
    }
    if history:
        latest = max((m.get("created_at", "") for m in history), default="")
        if latest:
            st.session_state.chat_last_ts_by_group[group_id] = latest


def _merge_new_messages(group_id: str, new_messages: list) -> int:
    """Append messages we haven't displayed yet, keeping the cache ordered
    oldest → newest. Returns the number of freshly-added messages.
    """
    if not new_messages:
        return 0

    cached = st.session_state.chat_messages_by_group.setdefault(group_id, [])
    seen = st.session_state.chat_seen_ids_by_group.setdefault(group_id, set())
    latest_ts = st.session_state.chat_last_ts_by_group.get(group_id, "")

    added = 0
    for msg in new_messages:
        msg_id = msg.get("id")
        if msg_id is not None and msg_id in seen:
            continue

        cached.append(msg)
        if msg_id is not None:
            seen.add(msg_id)
        added += 1

        created_at = msg.get("created_at") or ""
        if created_at and created_at > latest_ts:
            latest_ts = created_at

    if latest_ts:
        st.session_state.chat_last_ts_by_group[group_id] = latest_ts

    return added


def _format_time(created_at: str) -> str:
    if not created_at:
        return ""
    return str(created_at)[11:16]


@st.fragment(run_every=f"{POLL_INTERVAL_SECONDS}s")
def _chat_stream_fragment(group_id: str, user_id: str) -> None:
    """Auto-refreshing slice of the page. Streamlit reruns only this
    fragment every `POLL_INTERVAL_SECONDS` seconds, so new messages appear
    without a full page reload and without disturbing the input box.
    """
    last_ts = st.session_state.chat_last_ts_by_group.get(group_id)
    _merge_new_messages(group_id, get_new_messages(group_id, last_ts))

    messages = st.session_state.chat_messages_by_group.get(group_id, [])

    with st.container(height=450, border=True):
        if not messages:
            st.info("No messages yet. Start the conversation below.")
        else:
            for msg in messages:
                sender = msg.get("sender_id", "Unknown")
                content = msg.get("content", "")
                time_str = _format_time(msg.get("created_at", ""))
                is_me = sender == user_id

                role = "user" if is_me else "assistant"
                label = "You" if is_me else sender

                with st.chat_message(role):
                    st.markdown(
                        f"**{label}** · <span style='opacity:0.6'>{time_str}</span>",
                        unsafe_allow_html=True
                    )
                    st.write(content)


def display_group_chat_page() -> None:
    _init_group_chat_state()

    current_group = st.session_state.get("current_chat_group")
    user_id = (
        st.session_state.get("user_id")
        or st.session_state.get("current_user_id")
    )

    if not current_group:
        st.warning("No group selected.")
        return

    if not user_id:
        st.error("No logged-in user found.")
        return

    group_id = current_group.get("id")
    group_name = current_group.get("name", "Group Chat")

    if not group_id:
        st.error("Current group is missing an id.")
        return

    st.title(f"💬 {group_name}")
    st.caption(f"Live chat · updates every {POLL_INTERVAL_SECONDS}s")

    _prime_cache(group_id)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Refresh", use_container_width=True, key=f"gc_refresh_{group_id}"):
            # Hard refresh: drop the cache and reload the whole history.
            st.session_state.chat_messages_by_group.pop(group_id, None)
            st.session_state.chat_seen_ids_by_group.pop(group_id, None)
            st.session_state.chat_last_ts_by_group.pop(group_id, None)
            st.rerun()

    with col_b:
        if st.button("Back to My Groups", use_container_width=True, key=f"gc_back_{group_id}"):
            st.session_state.page = "My Groups"
            st.rerun()

    _chat_stream_fragment(group_id, user_id)

    message_text = st.chat_input(
        "Type a message…",
        key=f"chat_input_{group_id}",
    )

    if message_text and message_text.strip():
        try:
            send_message(group_id, user_id, message_text.strip())
            # Pull in the message we just wrote (and anything else that came
            # in while we were typing) so the UI updates instantly instead of
            # waiting for the next polling tick.
            last_ts = st.session_state.chat_last_ts_by_group.get(group_id)
            _merge_new_messages(group_id, get_new_messages(group_id, last_ts))
            st.rerun()
        except Exception as e:
            st.error(f"Failed to send message: {e}")

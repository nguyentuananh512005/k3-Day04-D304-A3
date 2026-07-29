from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from chat import (
    execute_tool_call,
    load_tool_declarations,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    to_openai_tools,
    trim_history,
    write_transcript,
)
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent Lab v2",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Research Agent Lab v2 — Interactive UI")
st.markdown("Hệ thống trợ lý nghiên cứu tự động thực thi công cụ & đo lường bằng chứng.")

# Sidebar Configuration
st.sidebar.header("⚙️ Cấu hình Agent")
provider_name = st.sidebar.selectbox("Model Provider", ["groq", "openrouter", "openai", "gemini"], index=0)
version_name = st.sidebar.selectbox("Phiên bản (Version)", ["v0", "v1", "v2", "v3"], index=3)
model_name = st.sidebar.text_input("Custom Model (Tùy chọn)", value="")
history_window = st.sidebar.slider("History Window", 1, 10, 5)
max_tool_rounds = st.sidebar.slider("Max Tool Rounds", 1, 8, 4)

# Load artifacts & build version
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

if system_prompt_path.exists() and tools_yaml_path.exists():
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_yaml_path)
    openai_tools = to_openai_tools(tool_declarations)
    art_ver = build_artifact_version(version_name, system_prompt_path, tools_yaml_path)
    st.sidebar.success(f"Artifact Version: `{art_ver.artifact_version}`")
    st.sidebar.caption(f"Prompt Hash: `{art_ver.prompt_hash[:8]}` | Tools Hash: `{art_ver.tools_hash[:8]}`")
else:
    st.error("Không tìm thấy tệp artifacts/system_prompt.md hoặc artifacts/tools.yaml")
    st.stop()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcript_id" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.transcript_id = f"{safe_slug(version_name)}_{safe_slug(provider_name)}_{timestamp}"
    st.session_state.transcript = {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(art_ver),
        "provider": provider_name,
        "model": model_name or "default",
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_yaml_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# Action Buttons
col_clear, col_export = st.sidebar.columns(2)
if col_clear.button("🗑️ Xóa Chat"):
    st.session_state.messages = []
    st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander("🛠️ Chi tiết Tool Trace (Thực thi công cụ)", expanded=False):
                for idx, event in enumerate(msg["tool_events"], 1):
                    st.markdown(f"**Step {idx}: `{event.get('tool')}`**")
                    st.json({"args": event.get("args"), "result": event.get("result")})

# Chat Input
user_input = st.chat_input("Nhập yêu cầu cho Research Agent...")
if user_input:
    # Render User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare Messages for Agent
    history = [m for m in st.session_state.messages if m["role"] in {"user", "assistant"}]
    working_messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history[:-1], history_window),
        {"role": "user", "content": user_input},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Agent đang suy nghĩ & thực thi công cụ..."):
            try:
                provider = make_provider(provider_name)
                result = run_model_tool_loop(
                    provider=provider,
                    messages=working_messages,
                    tools=openai_tools,
                    model=model_name or None,
                    max_tool_rounds=max_tool_rounds,
                )
                assistant_text = result.get("assistant_text", "")
                tool_events = result.get("tool_events", [])

                st.write(assistant_text)

                if tool_events:
                    with st.expander("🛠️ Chi tiết Tool Trace (Thực thi công cụ)", expanded=True):
                        for idx, event in enumerate(tool_events, 1):
                            st.markdown(f"**Step {idx}: `{event.get('tool')}`**")
                            st.json({"args": event.get("args"), "result": event.get("result")})

                # Append Assistant Message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": tool_events,
                })

                # Log Transcript
                turn_record = {
                    "turn_index": len(st.session_state.messages) // 2,
                    "started_at": now_iso(),
                    "user": user_input,
                    "status": result.get("status"),
                    "assistant_text": assistant_text,
                    "rounds": result.get("rounds"),
                    "tool_events": tool_events,
                    "ended_at": now_iso(),
                }
                st.session_state.transcript["turns"].append(turn_record)
                transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"
                write_transcript(transcript_path, st.session_state.transcript)
            except Exception as exc:
                st.error(f"Lỗi khi thực thi: {exc}")

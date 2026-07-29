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

# Paths Initialization
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
load_lab_env(ROOT)

# Page Setup
st.set_page_config(
    page_title="Research Agent Debut UI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 12px 18px;
        border: 1px solid #334155;
        text-align: center;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94A3B8;
    }
    .tool-badge {
        display: inline-block;
        background-color: #0F172A;
        color: #38BDF8;
        border: 1px solid #0284C7;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚀 Research Agent Debut — Interactive Console</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Trải nghiệm sức mạnh trợ lý nghiên cứu tự động thực thi công cụ & hội thoại thông minh</div>', unsafe_allow_html=True)

# Top Metric Banner
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-value">v2 (Optimized)</div><div class="metric-label">Phiên bản Agent</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-value">72.22%</div><div class="metric-label">Benchmark Accuracy</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div class="metric-value">100%</div><div class="metric-label">Multi-turn Accuracy</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><div class="metric-value">11 Tools</div><div class="metric-label">Công cụ khả dụng</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("⚙️ Bảng Điều Kiện Agent")

provider_name = st.sidebar.selectbox("Model Provider", ["groq", "openrouter", "openai", "gemini"], index=0)
version_name = st.sidebar.selectbox("Phiên bản Prompt & Tools", ["v0", "v1", "v2", "v3"], index=2) # Default v2
model_name = st.sidebar.text_input("Model Override (Tùy chọn)", value="")
history_window = st.sidebar.slider("Ngữ cảnh lịch sử (Turns)", 1, 10, 5)
max_tool_rounds = st.sidebar.slider("Giới hạn vòng gọi tool", 1, 8, 4)

# Load Artifacts
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

if system_prompt_path.exists() and tools_yaml_path.exists():
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_yaml_path)
    openai_tools = to_openai_tools(tool_declarations)
    art_ver = build_artifact_version(version_name, system_prompt_path, tools_yaml_path)
    st.sidebar.success(f"Version: `{art_ver.artifact_version}`")
else:
    st.error("Không tìm thấy tệp artifacts/system_prompt.md hoặc artifacts/tools.yaml")
    st.stop()

# Sidebar Transcript History (Load & View Past Sessions)
st.sidebar.markdown("---")
st.sidebar.subheader("📜 Lịch Sử Cuộc Trò Chuyện")
saved_transcripts = sorted(TRANSCRIPTS_DIR.glob("*.transcript.json"), reverse=True)

transcript_options = ["— Phiên làm việc hiện tại —"] + [f.name for f in saved_transcripts[:15]]
selected_transcript = st.sidebar.selectbox("Chọn phiên lưu trữ để xem lại", transcript_options, index=0)

if selected_transcript != "— Phiên làm việc hiện tại —":
    transcript_file = TRANSCRIPTS_DIR / selected_transcript
    try:
        t_data = json.loads(transcript_file.read_text(encoding="utf-8"))
        st.sidebar.caption(f"Tạo lúc: {t_data.get('created_at', 'N/A')}")
        st.sidebar.info(f"Tổng số turns: {len(t_data.get('turns', []))}")
    except Exception:
        pass

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
st.sidebar.markdown("---")
col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("✨ Chat Mới", use_container_width=True):
    st.session_state.messages = []
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
    st.rerun()

# Display Available Tools Badges
st.markdown("**🛠️ Danh sách Tool Agent đang sở hữu:**")
badges_html = "".join([f'<span class="tool-badge">🔧 {item["name"]}</span>' for item in tool_declarations])
st.markdown(badges_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Quick Preset Test Prompt Buttons
st.markdown("**⚡ Thử nhanh kịch bản Test sức mạnh Agent:**")
preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)

preset_query = None
if preset_col1.button("🌦️ Thời tiết Hà Nội", use_container_width=True):
    preset_query = "Thời tiết ở Hà Nội hôm nay thế nào?"
if preset_col2.button("❓ Thử thiếu Handle", use_container_width=True):
    preset_query = "Tóm tắt 5 tweet mới nhất giúp mình"
if preset_col3.button("📢 Thử gửi Telegram", use_container_width=True):
    preset_query = "Đăng bản tin tóm tắt này lên Telegram giúp mình"
if preset_col4.button("🚫 Thử câu Out-of-scope", use_container_width=True):
    preset_query = "Viết giúp mình một script Bash để tự động backup dữ liệu"

# Display Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander("🔍 Chi tiết Tool Trace (Thực thi ngầm)", expanded=False):
                for idx, event in enumerate(msg["tool_events"], 1):
                    st.markdown(f"**Lượt {idx}: Gọi Tool `{event.get('tool')}`**")
                    st.json({"arguments": event.get("args"), "result": event.get("result")})

# Handle User Input (Direct or Preset)
user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu cho Research Agent...") or preset_query

if user_input:
    # Render User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare Context History
    history = [m for m in st.session_state.messages if m["role"] in {"user", "assistant"}]
    working_messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history[:-1], history_window),
        {"role": "user", "content": user_input},
    ]

    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent đang suy luận & thực thi công cụ..."):
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
                    with st.expander("🔍 Chi tiết Tool Trace (Thực thi ngầm)", expanded=True):
                        for idx, event in enumerate(tool_events, 1):
                            st.markdown(f"**Lượt {idx}: Gọi Tool `{event.get('tool')}`**")
                            st.json({"arguments": event.get("args"), "result": event.get("result")})

                # Append Assistant Message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": tool_events,
                })

                # Save Transcript
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

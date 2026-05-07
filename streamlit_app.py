"""
Streamlit Web UI for LangGraph Research Agent
"""

import streamlit as st
import os

st.set_page_config(page_title="LangGraph Research Agent", layout="wide")

st.title("🤖 LangGraph Research Agent")
st.markdown(
    "Enter a research prompt and the agent will search the web, summarize, and provide an answer."
)

try:
    from main import run_agent
    MODE = "full"
    st.info("✓ Using LangChain + SerpAPI + Ollama/OpenAI")
except Exception as e:
    st.error(f"Error loading the main agent: {e}")
    st.stop()

# Check if API key is set (only needed for full mode)
if MODE == "full" and not os.getenv("SERPAPI_API_KEY"):
    st.error("❌ SERPAPI_API_KEY not set in environment!")
    st.info("Set it with: `setx SERPAPI_API_KEY your_key` (Windows) or `export SERPAPI_API_KEY=your_key` (Linux/Mac)")
    st.stop()

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar info
with st.sidebar:
    st.header("ℹ️ Configuration")
    st.write(f"Mode: **{MODE.upper()}**")
    
    if MODE == "full":
        use_local = os.getenv("USE_LOCAL_LLM", "true").lower() not in ("false", "0", "no")
        llm_type = "🟡 Local Ollama (llama2)" if use_local else "🟢 OpenAI"
        st.write(f"LLM: {llm_type}")
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    user_prompt = st.text_area(
        "Enter your research prompt:",
        height=100,
        placeholder="e.g., Research the latest trends in AI agents",
    )

with col2:
    st.markdown("### Options")
    run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)

# Process query
if run_button and user_prompt.strip():
    with st.spinner("🔄 Running LangGraph workflow..."):
        try:
            result = run_agent(user_prompt)
            st.session_state.history.append(
                {"prompt": user_prompt, "response": result}
            )

            st.success("✅ Complete!")
            st.markdown("### Agent Response")
            st.markdown(result)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display history
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📋 Query History")
    for i, item in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"Query {len(st.session_state.history) - i + 1}: {item['prompt'][:50]}..."):
            st.markdown(item["response"])

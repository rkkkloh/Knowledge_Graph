import streamlit as st
import subprocess
import sys
import os
import re
import time

# 頁面設定（與 app.py 一致）
st.set_page_config(page_title="Test Runner", page_icon="🛡️", layout="wide")

# 載入統一的 CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f. read()}</style>', unsafe_allow_html=True)

def execute_pytest(scope:  str):
    """Executes pytest subprocess based on the selected scope."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Base command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Scope filtering
    if scope == "UI / Frontend":
        cmd.append("test_ui.py")
    elif scope == "Backend / Logic":
        cmd.append("test_backend.py")
    
    # Verbose output for better parsing
    cmd.append("-v")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=root_dir
        )
        duration = time.time() - start_time
        return result, duration
    except Exception as e: 
        return None, 0

def parse_test_results(stdout: str):
    """Parses pytest stdout to extract metrics."""
    # Regex to find the summary line like "3 passed, 1 failed in 0.45s"
    summary_pattern = r"==+\s+(.*?)\s+in\s+([\d\. ]+)s"
    match = re.search(summary_pattern, stdout)
    
    stats = {"passed": 0, "failed":  0, "total": 0, "status": "Unknown"}
    
    if match: 
        summary = match.group(1)
        p_match = re.search(r"(\d+)\s+passed", summary)
        f_match = re.search(r"(\d+)\s+failed", summary)
        
        if p_match:  stats["passed"] = int(p_match.group(1))
        if f_match: stats["failed"] = int(f_match.group(1))
        stats["total"] = stats["passed"] + stats["failed"]
    
    # Fallback parsing if summary line is missing
    if stats["total"] == 0:
        stats["passed"] = stdout.count("PASSED")
        stats["failed"] = stdout.count("FAILED") + stdout.count("ERROR")
        stats["total"] = stats["passed"] + stats["failed"]

    return stats

# --- UI Layout ---

# 主標題（與 app.py 一致的白色標題）
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #FFFFFF; font-size: 2.5em;">
            🛡️ QA Test Runner
        </h1>
    </div>
""", unsafe_allow_html=True)

st.caption(f"Environment: Python {sys.version. split()[0]}")
st.markdown("---")

# Sidebar Configuration
with st.sidebar:
    st. header("Configuration")
    
    test_scope = st.radio(
        "Test Scope",
        ["All Tests", "UI / Frontend", "Backend / Logic"],
        index=0
    )
    
    st.markdown("---")
    
    if st.button("▶️ Run Tests", type="primary", use_container_width=True):
        st.session_state['run_triggered'] = True

# Main Content
if st.session_state. get('run_triggered', False):
    with st.spinner("Running tests..."):
        result, duration = execute_pytest(test_scope)
        
        if result is None:
            st.error("❌ Test execution failed")
        else:
            stats = parse_test_results(result. stdout)
            
            # Display Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tests", stats["total"])
            with col2:
                st. metric("Passed", stats["passed"], delta=None if stats["passed"] == 0 else f"+{stats['passed']}")
            with col3:
                st. metric("Failed", stats["failed"], delta=None if stats["failed"] == 0 else f"-{stats['failed']}", delta_color="inverse")
            with col4:
                st.metric("Duration", f"{duration:.2f}s")
            
            st.markdown("---")
            
            # Display Output
            st.subheader("📋 Test Output")
            with st.expander("View stdout", expanded=True):
                st. code(result.stdout, language="text")
            
            if result.stderr:
                with st.expander("View stderr"):
                    st.code(result.stderr, language="text")
            
            # Status
            if result.returncode == 0:
                st.success("✅ All tests passed!")
            else:
                st.error("❌ Some tests failed")
    
    st.session_state['run_triggered'] = False
else:
    st.info("👈 Configure settings in the sidebar and click 'Run Tests' to begin")
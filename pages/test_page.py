import streamlit as st
import subprocess
import sys
import os
import re
import time

# Page Configuration
st.set_page_config(page_title="Test Runner", page_icon="🛡️", layout="wide")

# Custom CSS for metric styling
st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def execute_pytest(scope: str):
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
    summary_pattern = r"==+\s+(.*?)\s+in\s+([\d\.]+)s"
    match = re.search(summary_pattern, stdout)
    
    stats = {"passed": 0, "failed": 0, "total": 0, "status": "Unknown"}
    
    if match:
        summary = match.group(1)
        p_match = re.search(r"(\d+)\s+passed", summary)
        f_match = re.search(r"(\d+)\s+failed", summary)
        
        if p_match: stats["passed"] = int(p_match.group(1))
        if f_match: stats["failed"] = int(f_match.group(1))
        stats["total"] = stats["passed"] + stats["failed"]
    
    # Fallback parsing if summary line is missing
    if stats["total"] == 0:
        stats["passed"] = stdout.count("PASSED")
        stats["failed"] = stdout.count("FAILED") + stdout.count("ERROR")
        stats["total"] = stats["passed"] + stats["failed"]

    return stats

# --- UI Layout ---

st.title("🛡️ QA Test Runner")
st.caption(f"Environment: Python {sys.version.split()[0]}")
st.markdown("---")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    
    test_scope = st.radio(
        "Test Scope",
        ["All Tests", "UI / Frontend", "Backend / Logic"],
        index=0
    )
    
    st.markdown("### Controls")
    if st.button("Run Tests", type="primary", use_container_width=True):
        run_triggered = True
    else:
        run_triggered = False

# Main Execution Logic
if run_triggered:
    with st.status("Initializing test environment...", expanded=True) as status:
        st.write("Targeting source files...")
        time.sleep(0.2) 
        st.write(f"Executing scope: **{test_scope}**")
        
        # Run
        result, duration = execute_pytest(test_scope)
        
        if result:
            stats = parse_test_results(result.stdout)
            
            if result.returncode == 0:
                status.update(label="Test Suite Completed Successfully", state="complete", expanded=False)
            else:
                status.update(label="Test Suite Failed", state="error", expanded=False)
        else:
            st.error("Failed to spawn pytest subprocess.")
            st.stop()

    # Metrics Dashboard
    cols = st.columns(4)
    cols[0].metric("Total Cases", stats['total'])
    cols[1].metric("Passed", stats['passed'])
    
    # Conditional styling for failed cases
    fail_color = "inverse" if stats['failed'] > 0 else "off"
    cols[2].metric("Failed", stats['failed'], delta=f"-{stats['failed']}" if stats['failed'] > 0 else None, delta_color=fail_color)
    
    cols[3].metric("Duration", f"{duration:.2f}s")

    st.markdown("---")

    # Result Details
    tab_overview, tab_logs, tab_traceback = st.tabs(["Overview", "Console Output", "Stack Trace"])

    with tab_overview:
        if result.returncode == 0:
            st.success("All systems operational.")
            # Extract test names for a cleaner list
            test_lines = [line.split("::")[1].split(" ")[0] for line in result.stdout.split('\n') if "::" in line]
            if test_lines:
                st.dataframe({"Passing Tests": test_lines}, use_container_width=True)
        else:
            st.error("Exceptions detected in the codebase.")

    with tab_logs:
        st.code(result.stdout, language="text")

    with tab_traceback:
        if stats['failed'] > 0 or result.stderr:
            st.warning("Traceback detected:")
            if result.stderr:
                st.code(result.stderr, language="bash")
            
            # Simple parsing to isolate failure blocks
            if "FAILED" in result.stdout:
                failures = result.stdout.split("FAILED")[1:]
                for f in failures:
                    # Clean up the output slightly
                    clean_log = f.split("===")[0].strip()
                    if clean_log:
                        st.text(clean_log)
                        st.divider()
        else:
            st.info("No tracebacks generated.")

else:
    st.info("Ready to execute. Click 'Run Tests' in the sidebar.")
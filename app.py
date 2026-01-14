import streamlit as st
import networkx as nx
from modules.backend import GraphManager
from modules.visualization import render_interactive_graph
from modules.ui import render_sidebar, render_main_tabs

# 1. 頁面設定
st.set_page_config(
    page_title="Nexus Graph | 互動式知識圖譜",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 初始化 Session State
if 'graph' not in st.session_state:
    manager = GraphManager()
    st.session_state['graph'] = manager.get_initial_graph()
    st.session_state['manager'] = manager
    # 清除舊快取
    if 'node_positions' in st.session_state:
        del st.session_state['node_positions']

with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 3. 主標題（改成白色）
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #FFFFFF; font-size: 2.5em;">
            🕸️ Nexus Graph 知識圖譜編輯器
        </h1>
    </div>
""", unsafe_allow_html=True)

# 4. 渲染側邊欄
render_sidebar()

# 5. 渲染分頁主功能區
render_main_tabs()

# 6. 渲染圖形
st.divider()
render_interactive_graph(st.session_state['graph'])
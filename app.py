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

# 3. 主標題
st.title("🕸️ Nexus Graph 知識圖譜編輯器")
st.markdown("---")

# 4. 渲染側邊欄
render_sidebar()

# 5. 主畫面佈局
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("📝 編輯資料")
    render_main_tabs()

with col_right:
    st.subheader("📊 知識圖譜視覺化")
    graph = st.session_state['graph']
    
    # 處理搜尋聚焦
    final_graph = graph
    # 確保 search_target 存在
    if 'search_target' in st.session_state and st.session_state['search_target'] != "(顯示全部)":
        target = st.session_state['search_target']
        neighbors = set(graph.successors(target)) | set(graph.predecessors(target))
        neighbors.add(target)
        final_graph = graph.subgraph(neighbors)
        st.info(f"🔍 聚焦於：{target}")

    if final_graph.number_of_nodes() > 0:
        render_interactive_graph(final_graph)
    else:
        st.info("目前沒有資料，請在左側新增角色！")
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("角色總數", graph.number_of_nodes())
    c2.metric("關係總數", graph.number_of_edges())
    c3.metric("密度", f"{nx.density(graph):.3f}")
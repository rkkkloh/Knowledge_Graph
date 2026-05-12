import streamlit as st
import networkx as nx
import json
import os
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
    
    # 嘗試載入範例檔案
    example_file = "data/example_harry_potter.json"
    if os.path.exists(example_file):
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            graph = nx.DiGraph()
            for node in data.get('nodes', []):
                graph.add_node(
                    node['id'],
                    label=node.get('label', node['id']),
                    title=node.get('title', ''),
                    chapter=node.get('chapter', 1) 
                )
            for edge in data.get('edges', []):
                graph.add_edge(
                    edge['from'],
                    edge['to'],
                    label=edge.get('label', ''),
                    chapter=edge.get('chapter', 1),
                    timeline=edge.get('timeline', {"1": {'label': edge.get('label', ''), 'color': '#4CAF50'}})
                )
            
            st.session_state['graph'] = graph
            st.session_state['example_loaded'] = True
        except Exception as e:
            st.session_state['graph'] = manager.get_initial_graph()
            st.session_state['example_loaded'] = False
            st.error(f"範例載入失敗：{e}")
    else:
        st.session_state['graph'] = manager.get_initial_graph()
        st.session_state['example_loaded'] = False
    
    st.session_state['manager'] = manager
    if 'node_positions' in st.session_state:
        del st.session_state['node_positions']

# 載入 CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 3. 主標題
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #FFFFFF; font-size: 2.5em;">
            🕸️ Nexus Graph 知識圖譜編輯器
        </h1>
    </div>
""", unsafe_allow_html=True)

if st.session_state.get('example_loaded') and 'example_toast_shown' not in st.session_state:
    st.toast("✨ 已載入哈利波特範例圖譜！", icon="📚")
    st.session_state['example_toast_shown'] = True

# 4. 渲染側邊欄與主功能區
render_sidebar()
render_main_tabs()

# 5. 渲染圖形區塊與 ⏳ 通用時間軸
st.divider()

graph = st.session_state['graph']
max_chapter = 1
for _, data in graph.nodes(data=True):
    max_chapter = max(max_chapter, data.get('chapter', 1))
for _, _, data in graph.edges(data=True):
    max_chapter = max(max_chapter, data.get('chapter', 1))

# 通用版時間拉桿
selected_chapter = st.slider("⏳ 時間演進 (可為年份、章節或自訂階段)", min_value=1, max_value=max(2, max_chapter), value=max_chapter)

# 打造帶有記憶功能的時間軸視角
timeline_graph = nx.DiGraph()

# 1. 篩選符合時間的節點
for n, data in graph.nodes(data=True):
    if data.get('chapter', 1) <= selected_chapter:
        timeline_graph.add_node(n, **data)

# 2. 篩選連線，並重現「當時的顏色與標籤」
for u, v, data in graph.edges(data=True):
    orig_chap = data.get('chapter', 1)
    timeline = data.get('timeline', {str(orig_chap): {'label': data.get('label'), 'color': data.get('color', '#9E9E9E')}})
    
    # 找出該時間點之前，所有的歷史紀錄
    valid_chapters = [int(c) for c in timeline.keys() if int(c) <= selected_chapter]
    
    if valid_chapters:
        latest_valid_chapter = max(valid_chapters)
        state = timeline[str(latest_valid_chapter)]
        timeline_graph.add_edge(u, v, label=state.get('label', ''), color=state.get('color', '#9E9E9E'))

# 繪製圖表
render_interactive_graph(timeline_graph)
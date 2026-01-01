import streamlit as st
import networkx as nx
from modules.backend import GraphManager
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os

# 1. 頁面設定
st.set_page_config(
    page_title="Nexus Graph | 互動式知識圖譜",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 輔助函式：繪製 PyVis 圖表 (視覺化核心) ---
def render_interactive_graph(nx_graph, physics_enabled=True):
    """
    將 NetworkX 圖轉換為 PyVis HTML 並在 Streamlit 中顯示
    """
    # 1. 建立 PyVis 网络物件
    # ✅ 修改：加入 directed=True 確保 PyVis 知道這是要畫箭頭的有向圖
    net = Network(height="600px", width="100%", bgcolor="#222831", font_color="white", directed=True)
    
    # 2. 載入 NetworkX 資料
    net.from_nx(nx_graph)
    
    # 3. 設置物理引擎與樣式 (使用您提供的專業設定)
    # 這裡加入了 arrows 設定與 smooth (curvedCW) 以支援雙向顯示
    base_options = """
    var options = {
      "nodes": {
        "borderWidth": 2,
        "color": {
          "highlight": {
            "border": "#00ADB5",
            "background": "#393E46"
          }
        },
        "font": { "size": 16, "face": "tahoma" }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1
          }
        },
        "color": { "inherit": true },
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.2
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """
    
    # 如果使用者選擇關閉物理引擎，我們強制覆寫 physics 設定
    if not physics_enabled:
        net.toggle_physics(False)
        # ✅ 修改：即使關閉物理，我們還是保留 arrows 和 smooth 設定，不然圖會變醜且沒箭頭
        net.set_options("""
        var options = {
          "edges": {
            "arrows": { "to": { "enabled": true } },
            "smooth": { "type": "curvedCW", "roundness": 0.2 }
          },
          "physics": { "enabled": false }
        }
        """)
    else:
        # 啟用完整的物理引擎設定 (包含您提供的字串)
        net.set_options(base_options)
    
    try:
        # 4. 生成與顯示 HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.save_graph(tmp_file.name)
            tmp_file.seek(0)
            html_content = tmp_file.read().decode('utf-8')
        
        components.html(html_content, height=610, scrolling=False)
        os.unlink(tmp_file.name)
    except Exception as e:
        st.error(f"圖表繪製失敗: {e}")

# 2. 初始化 Session State
if 'graph' not in st.session_state:
    manager = GraphManager()
    st.session_state['graph'] = manager.get_initial_graph()
    st.session_state['manager'] = manager

# 3. 標題區
st.title("🕸️ Nexus Graph 知識圖譜編輯器")
st.markdown("---")

# 4. 側邊欄 (專案控制)
with st.sidebar:
    st.header("🎛️ 專案控制台")
    # st.info("目前模式：Mocking (模擬後端)") # 如果已經接了 API，這行可以註解掉

    st.header("🔑 API 設定")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if not api_key:
        st.warning("⚠️ 請輸入 API Key 才能使用 AI 功能")
    
    st.markdown("---")
    
    # 專案存檔區塊
    with st.expander("💾 專案管理 (Save/Load)", expanded=True):
        st.caption("儲存專案")
        col_save_1, col_save_2 = st.columns([2, 1])
        with col_save_1:
            project_name = st.text_input("專案檔名", value="my_story", label_visibility="collapsed")
        with col_save_2:
            if st.button("Save", use_container_width=True):
                success, msg = st.session_state['manager'].save_graph(st.session_state['graph'], project_name)
                if success:
                    st.toast(msg, icon="💾")
                else:
                    st.error(msg)

        st.markdown("---")
        st.header("👀 檢視設定")
        
        # 1. 搜尋功能
        all_nodes = list(st.session_state['graph'].nodes())
        search_target = st.selectbox("🔍 搜尋並聚焦角色", ["(顯示全部)"] + all_nodes)
        
        # 2. 物理引擎開關
        use_physics = st.toggle("啟動物理引擎 (動畫)", value=True)
        
        st.markdown("---")
        
        # 3. 讀檔功能
        st.caption("載入舊專案")
        uploaded_file = st.file_uploader("選擇 JSON 檔案", type="json", label_visibility="collapsed")
        
        if uploaded_file is not None:
            if st.button("Load Project", use_container_width=True):
                new_graph, msg = st.session_state['manager'].load_graph(uploaded_file)
                if new_graph:
                    st.session_state['graph'] = new_graph
                    st.toast(msg, icon="📂")
                    st.rerun()
                else:
                    st.error(msg)
    
    st.markdown("---")
    st.caption("Designed by Group B")

# 5. 主畫面佈局
col_left, col_right = st.columns([1, 2], gap="large")

# === 左側：編輯區 ===
with col_left:
    st.subheader("📝 編輯資料")
    
    # 定義四個 Tabs
    tab_char, tab_rel, tab_ai, tab_manage = st.tabs(["👤 新增", "🔗 連結", "🤖 AI", "⚙️ 管理"])
    
    # --- Tab 1: 新增角色 ---
    with tab_char:
        with st.form("char_form", clear_on_submit=True):
            c_name = st.text_input("角色名稱 (必填)", placeholder="例如：哈利波特")
            c_desc = st.text_area("角色描述", placeholder="例如：葛來分多的學生...")
            if st.form_submit_button("✨ 加入角色", use_container_width=True):
                if not c_name:
                    st.error("❌ 請輸入角色名稱！")
                else:
                    success, msg = st.session_state['manager'].add_character(
                        st.session_state['graph'], c_name, c_desc
                    )
                    if success: st.toast(msg, icon="✅")
                    else: st.error(msg)

    # --- Tab 2: 建立關係 ---
    with tab_rel:
        st.caption("提示：請先確認角色已存在於圖譜中")
        with st.form("rel_form", clear_on_submit=True):
            current_nodes = list(st.session_state['graph'].nodes())
            c1, c2 = st.columns(2)
            with c1: source = st.selectbox("來源角色", options=current_nodes, key="src_select")
            with c2: target = st.selectbox("目標角色", options=current_nodes, key="tgt_select")
            relation = st.text_input("關係類型", placeholder="例如：朋友、敵人")
            
            if st.form_submit_button("🔗 建立連結", use_container_width=True):
                if source == target: st.warning("⚠️ 來源與目標不能是同一個人！")
                elif not relation: st.error("❌ 請輸入關係類型！")
                else:
                    success, msg = st.session_state['manager'].add_relationship(
                        st.session_state['graph'], source, target, relation
                    )
                    if success: st.toast(msg, icon="🔗")
                    else: st.error(msg)

    # --- Tab 3: AI 介面 ---
    with tab_ai:
        st.caption("貼上故事文本，讓 AI 自動幫您分析")
        source_text = st.text_area("故事文本", height=150, placeholder="請貼上一段小說內容...")
        
        if st.button("🚀 開始分析 (Real AI)", use_container_width=True):
            if not source_text:
                st.warning("⚠️ 請先貼上文章內容！")
            elif not api_key:
                st.error("❌ 尚未設定 OpenAI API Key！")
            else:
                with st.spinner("🤖 AI 正在分析關係..."):
                    ai_nodes, ai_edges, error = st.session_state['manager'].process_text_with_ai(source_text, api_key)
                    if error: st.error(f"AI 呼叫失敗：{error}")
                    else:
                        st.session_state['ai_result'] = {"nodes": ai_nodes, "edges": ai_edges}
                        st.toast("分析完成！", icon="✅")

        if 'ai_result' in st.session_state:
            res = st.session_state['ai_result']
            st.divider()
            st.markdown("#### 🕵️ 審核結果")
            st.dataframe(res['nodes'], use_container_width=True)
            st.dataframe(res['edges'], use_container_width=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ 確認匯入", type="primary", use_container_width=True):
                    msg = st.session_state['manager'].batch_import(st.session_state['graph'], res['nodes'], res['edges'])
                    st.success(msg)
                    del st.session_state['ai_result']
                    st.rerun()
            with b2:
                if st.button("🗑️ 放棄", use_container_width=True):
                    del st.session_state['ai_result']
                    st.rerun()

    # --- Tab 4: 管理介面 (整合後端刪除/編輯功能) ---
    with tab_manage:
        st.caption("修正或刪除既有的資料")
        
        # 刪除區塊
        with st.expander("🗑️ 刪除資料", expanded=True):
            del_type = st.radio("欲刪除的項目", ["角色", "關係"], horizontal=True)
            
            if del_type == "角色":
                del_node = st.selectbox("選擇要刪除的角色", options=list(st.session_state['graph'].nodes()), key="del_node")
                if st.button("確認刪除角色", type="primary", use_container_width=True):
                    success, msg = st.session_state['manager'].delete_character(st.session_state['graph'], del_node)
                    if success:
                        st.toast(msg, icon="🗑️")
                        st.rerun()
                    else:
                        st.error(msg)
            
            elif del_type == "關係":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options:
                    st.info("目前沒有任何關係")
                else:
                    del_edge_str = st.selectbox("選擇要刪除的關係", options=edge_options, key="del_edge")
                    if st.button("確認刪除關係", type="primary", use_container_width=True):
                        u, v = del_edge_str.split(" -> ")
                        success, msg = st.session_state['manager'].delete_relationship(st.session_state['graph'], u, v)
                        if success:
                            st.toast(msg, icon="🗑️")
                            st.rerun()
                        else:
                            st.error(msg)

        # 編輯區塊
        with st.expander("✏️ 修改資料", expanded=False):
            edit_type = st.radio("欲修改的項目", ["角色描述", "關係標籤"], horizontal=True)
            
            if edit_type == "角色描述":
                edit_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="edit_node")
                current_desc = st.session_state['graph'].nodes[edit_node].get('title', '')
                new_desc = st.text_area("更新描述", value=current_desc)
                if st.button("更新角色資料", use_container_width=True):
                    success, msg = st.session_state['manager'].edit_character_description(st.session_state['graph'], edit_node, new_desc)
                    if success:
                        st.toast(msg, icon="✏️")
                        st.rerun()
                    else: st.error(msg)
            
            elif edit_type == "關係標籤":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options:
                    st.info("目前沒有任何關係")
                else:
                    edit_edge_str = st.selectbox("選擇關係", options=edge_options, key="edit_edge")
                    u, v = edit_edge_str.split(" -> ")
                    current_label = st.session_state['graph'][u][v].get('label', '')
                    new_label = st.text_input("更新關係類型 (Label)", value=current_label)
                    if st.button("更新關係", use_container_width=True):
                        success, msg = st.session_state['manager'].edit_relationship_label(st.session_state['graph'], u, v, new_label)
                        if success:
                            st.toast(msg, icon="✏️")
                            st.rerun()
                        else: st.error(msg)

# === 右側：視覺化與分析區 ===
with col_right:
    st.subheader("📊 知識圖譜視覺化")
    
    graph = st.session_state['graph']
    nodes_count = graph.number_of_nodes()
    edges_count = graph.number_of_edges()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("角色", nodes_count, delta=f"+{nodes_count}")
    c2.metric("關係", edges_count)
    density = nx.density(graph)
    c3.metric("密度", f"{density:.3f}")
    
    st.markdown("---")
    
    # 搜尋聚焦邏輯
    final_graph = st.session_state['graph']
    if 'search_target' not in locals() and 'search_target' not in globals():
         search_target = "(顯示全部)"

    if search_target != "(顯示全部)":
        target = search_target
        # DiGraph 需同時考慮出入邊
        neighbors = set(final_graph.successors(target)) | set(final_graph.predecessors(target))
        neighbors.add(target)
        final_graph = final_graph.subgraph(neighbors)
        st.info(f"🔍 目前聚焦於：{target}")

    # 繪圖 (使用更新後的設定)
    if final_graph.number_of_nodes() > 0:
        with st.spinner("正在渲染圖譜..."):
            render_interactive_graph(final_graph, physics_enabled=use_physics)
    else:
        st.info("目前沒有資料，請在左側新增角色！")
    
    with st.expander("ℹ️ 操作說明"):
        st.markdown("""
        - **縮放/移動**：滾輪與拖曳
        - **物理引擎**：可在左側關閉
        - **箭頭**：現在支援有向顯示！
        """)
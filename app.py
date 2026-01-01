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

# --- 輔助函式：繪製 PyVis 圖表 ---
def render_interactive_graph(nx_graph, physics_enabled=True):
    """
    將 NetworkX 圖轉換為 PyVis HTML 並在 Streamlit 中顯示
    新增參數: physics_enabled (布林值) - 控制是否啟用物理引擎
    """
    net = Network(height="600px", width="100%", bgcolor="#222831", font_color="white")
    net.from_nx(nx_graph)
    
    # 根據參數決定物理引擎設定
    if physics_enabled:
        net.set_options("""
        var options = {
          "nodes": {
            "borderWidth": 2,
            "color": { "highlight": { "border": "#00ADB5", "background": "#393E46" } },
            "font": { "size": 16, "face": "tahoma" }
          },
          "edges": { "color": { "inherit": true }, "smooth": false },
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
        """)
    else:
        # 關閉物理引擎 (固定位置模式)
        net.toggle_physics(False)
        net.set_options("""
        var options = {
          "nodes": {
            "borderWidth": 2,
            "color": { "highlight": { "border": "#00ADB5", "background": "#393E46" } },
            "font": { "size": 16, "face": "tahoma" }
          },
          "edges": { "color": { "inherit": true }, "smooth": false }
        }
        """)
    
    try:
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
    st.info("目前模式：Mocking (模擬後端)")

    st.header("🔑 API 設定")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if not api_key:
        st.warning("⚠️ 請輸入 API Key 才能使用 AI 功能")
    
    st.markdown("---")
    
    # 專案存檔區塊
    with st.expander("💾 專案管理 (Save/Load)", expanded=True):
        # 1. 存檔功能
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
        
        # 1. 搜尋功能 (Task 2)
        # 取得所有角色清單，並加入一個 "無 (顯示全部)" 的選項
        all_nodes = list(st.session_state['graph'].nodes())
        search_target = st.selectbox("🔍 搜尋並聚焦角色", ["(顯示全部)"] + all_nodes)
        
        # 2. 物理引擎開關 (Task 3)
        use_physics = st.toggle("啟動物理引擎 (動畫)", value=True)
        
        st.markdown("---")
        
        # 2. 讀檔功能 (新增的部分)
        st.caption("載入舊專案")
        uploaded_file = st.file_uploader("選擇 JSON 檔案", type="json", label_visibility="collapsed")
        
        if uploaded_file is not None:
            # 避免重複載入，可以檢查 session state 或直接執行
            if st.button("Load Project", use_container_width=True):
                new_graph, msg = st.session_state['manager'].load_graph(uploaded_file)
                if new_graph:
                    st.session_state['graph'] = new_graph
                    st.toast(msg, icon="📂")
                    st.rerun() # 重新整理頁面以顯示新圖
                else:
                    st.error(msg)
    
    st.markdown("---")
    st.caption("Designed by Group B")

# 5. 主畫面佈局
col_left, col_right = st.columns([1, 2], gap="large")

# === 左側：編輯區 (您的核心工作) ===
with col_left:
    st.subheader("📝 編輯資料")
    
    # 【修改】變成四個 Tabs
    tab_char, tab_rel, tab_ai, tab_manage = st.tabs(["👤 新增", "🔗 連結", "🤖 AI", "⚙️ 管理"])
    
    # --- Tab 1: 角色表單 ---
    with tab_char:
        with st.form("char_form", clear_on_submit=True):
            c_name = st.text_input("角色名稱 (必填)", placeholder="例如：哈利波特")
            c_desc = st.text_area("角色描述", placeholder="例如：葛來分多的學生...")
            
            # 送出按鈕
            submitted = st.form_submit_button("✨ 加入角色", use_container_width=True)
            
            if submitted:
                if not c_name:
                    st.error("❌ 請輸入角色名稱！")
                else:
                    # 呼叫後端
                    success, msg = st.session_state['manager'].add_character(
                        st.session_state['graph'], c_name, c_desc
                    )
                    if success:
                        st.toast(msg, icon="✅") # 使用 Toast 彈出式訊息，更現代
                    else:
                        st.error(msg)

    # --- Tab 2: 關係表單 ---
    with tab_rel:
        st.caption("提示：請先確認角色已存在於圖譜中")
        with st.form("rel_form", clear_on_submit=True):
            # 獲取目前所有角色清單 (給使用者選，防止打錯字)
            current_nodes = list(st.session_state['graph'].nodes())
            
            c1, c2 = st.columns(2)
            with c1:
                source = st.selectbox("來源角色", options=current_nodes, key="src_select")
            with c2:
                target = st.selectbox("目標角色", options=current_nodes, key="tgt_select")
            
            relation = st.text_input("關係類型", placeholder="例如：朋友、敵人、師徒")
            
            submitted_rel = st.form_submit_button("🔗 建立連結", use_container_width=True)
            
            if submitted_rel:
                if source == target:
                    st.warning("⚠️ 來源與目標不能是同一個人！")
                elif not relation:
                    st.error("❌ 請輸入關係類型！")
                else:
                    success, msg = st.session_state['manager'].add_relationship(
                        st.session_state['graph'], source, target, relation
                    )
                    if success:
                        st.toast(msg, icon="🔗")
                    else:
                        st.error(msg)

    # --- 【新增】Tab 3: AI 介面 ---
    with tab_ai:
        st.caption("貼上故事文本，讓 AI 自動幫您分析人物關係")
        
        # 1. 輸入區
        source_text = st.text_area("故事文本", height=150, placeholder="請貼上一段小說內容...")
        
        if st.button("🚀 開始分析 (Real AI)", use_container_width=True):
            if not source_text:
                st.warning("⚠️ 請先貼上文章內容！")
            elif not api_key:
                st.error("❌ 尚未設定 OpenAI API Key！請在左側欄位輸入。")
            else:
                with st.spinner("🤖 AI 正在閱讀故事並分析關係 (這可能需要幾秒鐘)..."):
                    # 呼叫真實的後端函式
                    ai_nodes, ai_edges, error = st.session_state['manager'].process_text_with_ai(source_text, api_key)
                    
                    if error:
                        st.error(f"AI 呼叫失敗：{error}")
                    else:
                        # 將結果暫存在 session_state
                        st.session_state['ai_result'] = {"nodes": ai_nodes, "edges": ai_edges}
                        st.toast("分析完成！請往下確認結果", icon="✅")

        # 2. 結果審核區 (如果有分析結果才顯示)
        if 'ai_result' in st.session_state:
            res = st.session_state['ai_result']
            
            st.divider()
            st.markdown("#### 🕵️ 審核分析結果")
            
            # 顯示預覽表格 (使用 dataframe 比較美觀)
            st.markdown("**發現的角色：**")
            st.dataframe(res['nodes'], use_container_width=True)
            
            st.markdown("**發現的關係：**")
            st.dataframe(res['edges'], use_container_width=True)
            
            # 確認匯入按鈕
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("✅ 確認匯入圖譜", type="primary", use_container_width=True):
                    msg = st.session_state['manager'].batch_import(
                        st.session_state['graph'], res['nodes'], res['edges']
                    )
                    st.success(msg)
                    # 清除暫存
                    del st.session_state['ai_result']
                    st.rerun() # 重新整理頁面以顯示新圖
            
            with btn_col2:
                if st.button("🗑️ 放棄結果", use_container_width=True):
                    del st.session_state['ai_result']
                    st.rerun()

    # --- 【新增】Tab 4: 管理介面 (Task 1) ---
    with tab_manage:
        st.caption("修正或刪除既有的資料")
        
        # 區塊 A: 刪除功能
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
                # 製作 "來源 -> 目標" 的清單供選擇
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

        # 區塊 B: 編輯功能
        with st.expander("✏️ 修改資料", expanded=False):
            edit_type = st.radio("欲修改的項目", ["角色描述", "關係標籤"], horizontal=True)
            
            if edit_type == "角色描述":
                edit_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="edit_node")
                # 預設填入目前的描述
                current_desc = st.session_state['graph'].nodes[edit_node].get('title', '')
                new_desc = st.text_area("更新描述", value=current_desc)
                
                if st.button("更新角色資料", use_container_width=True):
                    success, msg = st.session_state['manager'].edit_character_description(st.session_state['graph'], edit_node, new_desc)
                    if success:
                        st.toast(msg, icon="✏️")
                        st.rerun()
                    else:
                        st.error(msg)
            
            elif edit_type == "關係標籤":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options:
                    st.info("目前沒有任何關係")
                else:
                    edit_edge_str = st.selectbox("選擇關係", options=edge_options, key="edit_edge")
                    u, v = edit_edge_str.split(" -> ")
                    # 取得目前的標籤
                    current_label = st.session_state['graph'][u][v].get('label', '')
                    new_label = st.text_input("更新關係類型 (Label)", value=current_label)
                    
                    if st.button("更新關係", use_container_width=True):
                        success, msg = st.session_state['manager'].edit_relationship_label(st.session_state['graph'], u, v, new_label)
                        if success:
                            st.toast(msg, icon="✏️")
                            st.rerun()
                        else:
                            st.error(msg)

# === 右側：視覺化與分析區 ===
with col_right:
    st.subheader("📊 知識圖譜視覺化")
    
    # 顯示統計數據 (Metrics)
    graph = st.session_state['graph']
    nodes_count = graph.number_of_nodes()
    edges_count = graph.number_of_edges()
    
    # 這些卡片顯示在圖的上方
    c1, c2, c3 = st.columns(3)
    c1.metric("角色", nodes_count, delta=f"+{nodes_count} (Total)")
    c2.metric("關係", edges_count, help="目前的連結總數")
    
    # 計算密度
    density = nx.density(graph)
    c3.metric("圖譜密度", f"{density:.3f}", help="數值越高代表關係越緊密")
    
    st.markdown("---")
    
    # ⚠️【修正點】：這裡原本有一段舊的 render_interactive_graph(graph)，請確保已刪除！
    
    # 1. 決定要畫哪一張圖 (全圖 vs 搜尋結果)
    final_graph = st.session_state['graph'] # 預設畫全圖
    
    # 確保搜尋變數存在 (防呆)
    if 'search_target' not in locals() and 'search_target' not in globals():
         search_target = "(顯示全部)"

    if search_target != "(顯示全部)":
        # 建立子圖：只包含目標節點 + 它的鄰居
        target = search_target
        # 找鄰居 (因為是有向圖，要找 predecessors 和 successors)
        neighbors = set(final_graph.successors(target)) | set(final_graph.predecessors(target))
        neighbors.add(target) # 把自己也加進去
        final_graph = final_graph.subgraph(neighbors)
        st.info(f"🔍 目前聚焦於：{target} (及其關聯角色)")

    # 2. 呼叫視覺化函式 (傳入物理開關)
    if final_graph.number_of_nodes() > 0:
        with st.spinner("正在運算物理佈局..."):
            # 這裡使用新的邏輯，並傳入物理開關參數
            render_interactive_graph(final_graph, physics_enabled=use_physics)
    else:
        st.info("目前沒有資料，請在左側新增角色來開始！")
    
    # 額外功能：顯示圖例或說明
    with st.expander("ℹ️ 操作說明"):
        st.markdown("""
        - **縮放**：使用滑鼠滾輪
        - **移動**：點擊空白處拖曳
        - **選取**：點擊角色可高亮顯示
        - **調整**：您可以拖曳節點來改變位置
        """)
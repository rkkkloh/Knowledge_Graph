import streamlit as st
import networkx as nx
from modules.backend import GraphManager
# 👇 關鍵修改：從新的模組匯入視覺化函式
from modules.visualization import render_interactive_graph 
import streamlit.components.v1 as components

# 設定頁面配置
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
    # 確保移除舊的 node_positions，改用 JS 控制
    if 'node_positions' in st.session_state:
        del st.session_state['node_positions']

# 3. 標題區
st.title("🕸️ Nexus Graph 知識圖譜編輯器")
st.markdown("---")

# 4. 側邊欄與功能區
with st.sidebar:
    st.header("🎛️ 專案控制台")

    st.header("🔑 API 設定")
    st.info("💡 尚未擁有 Key？點擊下方按鈕免費產生：")
    st.link_button("👉 產生 Groq API Key (免費)", "https://console.groq.com/keys")
    
    api_key = st.text_input("輸入 API Key (貼上 gsk_...)", type="password", placeholder="gsk_...")
    
    if api_key:
        st.caption("✅ 已輸入 Key")
    else:
        st.warning("⚠️ 請輸入 Key 以啟用 AI 功能")
    
    st.markdown("---")
    
    with st.expander("💾 專案管理", expanded=True):
        col_save_1, col_save_2 = st.columns([2, 1])
        with col_save_1:
            project_name = st.text_input("專案檔名", value="my_story", label_visibility="collapsed")
        with col_save_2:
            if st.button("Save", width="stretch"):
                success, msg = st.session_state['manager'].save_graph(st.session_state['graph'], project_name)
                if success: st.toast(msg, icon="💾")
                else: st.error(msg)

        st.markdown("---")
        st.header("👀 檢視設定")
        
        all_nodes = list(st.session_state['graph'].nodes())
        search_target = st.selectbox("🔍 搜尋並聚焦角色", ["(顯示全部)"] + all_nodes)
        
        # 重置按鈕：清除 JS LocalStorage 記憶
        if st.button("🔄 重置視角與位置"):
            components.html("""
            <script>
                localStorage.removeItem("nexus_graph_positions");
                localStorage.removeItem("nexus_graph_camera");
                window.parent.location.reload();
            </script>
            """, height=0)
            st.rerun()
            
        st.markdown("---")
        
        uploaded_file = st.file_uploader("選擇 JSON 檔案", type="json", label_visibility="collapsed")
        if uploaded_file is not None:
            if st.button("Load Project", width="stretch"):
                new_graph, msg = st.session_state['manager'].load_graph(uploaded_file)
                if new_graph:
                    st.session_state['graph'] = new_graph
                    # 讀檔時清除舊記憶，避免座標錯亂
                    components.html("""
                    <script>
                        localStorage.removeItem("nexus_graph_positions");
                        localStorage.removeItem("nexus_graph_camera");
                        window.parent.location.reload();
                    </script>
                    """, height=0)
                    st.toast(msg, icon="📂")
                else:
                    st.error(msg)
    
    st.caption("Designed by Group B")

# 5. 主畫面佈局
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("📝 編輯資料")
    tab_char, tab_rel, tab_ai, tab_manage = st.tabs(["👤 新增", "🔗 連結", "🤖 AI", "⚙️ 管理"])
    
    # Tab 1: 新增角色
    with tab_char:
        with st.form("char_form", clear_on_submit=True):
            c_name = st.text_input("角色名稱 (必填)", placeholder="例如：哈利波特")
            c_desc = st.text_area("角色描述", placeholder="例如：葛來分多的學生...")
            if st.form_submit_button("✨ 加入角色", width="stretch"):
                if not c_name: st.error("❌ 請輸入角色名稱！")
                else:
                    success, msg = st.session_state['manager'].add_character(
                        st.session_state['graph'], c_name, c_desc
                    )
                    if success:
                        st.toast(msg, icon="✅")
                    else:
                        st.error(msg)

    # Tab 2: 建立連結
    with tab_rel:
        with st.form("rel_form", clear_on_submit=True):
            # 獲取目前所有角色清單
            current_nodes = list(st.session_state['graph'].nodes())
            
            if not current_nodes:
                st.warning("⚠️ 請先新增角色！")
                st.form_submit_button("🔗 建立連結", disabled=True)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    source = st.selectbox("來源角色", options=current_nodes, key="src_select")
                with c2:
                    target = st.selectbox("目標角色", options=current_nodes, key="tgt_select")
                
                relation = st.text_input("關係類型", placeholder="例如：朋友、敵人、師徒")
                
                if st.form_submit_button("🔗 建立連結", width="stretch"):
                    if source == target: st.warning("⚠️ 來源與目標不能是同一個人！")
                    elif not relation: st.error("❌ 請輸入關係類型！")
                    else:
                        success, msg = st.session_state['manager'].add_relationship(
                            st.session_state['graph'], source, target, relation
                        )
                        if success:
                            st.toast(msg, icon="🔗")
                        else:
                            st.error(msg)

    # Tab 3: AI 分析
    with tab_ai:
        st.caption("支援 OpenAI 與 Groq (貼上 Key 即可自動切換)")
        source_text = st.text_area("故事文本", height=150, placeholder="請貼上一段小說內容...")
        
        if st.button("🚀 開始分析", width="stretch"):
            if not source_text: st.warning("⚠️ 請先貼上文章內容！")
            elif not api_key: st.error("❌ 尚未設定 API Key！")
            else:
                with st.spinner("🤖 AI 正在分析關係..."):
                    ai_nodes, ai_edges, error = st.session_state['manager'].process_text_with_ai(source_text, api_key)
                    
                    # 處理 AI 回傳空值的情況
                    if not ai_nodes and not ai_edges and not error:
                        st.warning("🤔 AI 沒有在文本中找到任何角色或關係。請嘗試輸入更完整的句子。")
                    elif error: 
                        st.error(f"AI 呼叫失敗：{error}")
                    else:
                        st.session_state['ai_result'] = {"nodes": ai_nodes, "edges": ai_edges}
                        st.toast("分析完成！", icon="✅")

        # 結果審核區
        if 'ai_result' in st.session_state:
            res = st.session_state['ai_result']
            st.divider()
            st.markdown("#### 🕵️ 審核結果")
            st.dataframe(res['nodes'], use_container_width=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ 確認匯入", type="primary", width="stretch", key="btn_confirm_ai"):
                    msg = st.session_state['manager'].batch_import(st.session_state['graph'], res['nodes'], res['edges'])
                    st.toast(msg, icon="✅")
                    del st.session_state['ai_result']
                    st.rerun()
            with b2:
                if st.button("🗑️ 放棄", width="stretch", key="btn_cancel_ai"):
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

    # Tab 4: 資料管理 (新增的第四個分頁)
    with tab_manage:
        with st.expander("🗑️ 刪除資料", expanded=True):
            del_type = st.radio("欲刪除的項目", ["角色", "關係"], horizontal=True)
            if del_type == "角色":
                del_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="del_node")
                if st.button("確認刪除", type="primary", width="stretch"):
                    success, msg = st.session_state['manager'].delete_character(st.session_state['graph'], del_node)
                    if success: st.toast(msg, icon="🗑️"); st.rerun()
                    else: st.error(msg)
            elif del_type == "關係":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options: st.info("無關係可刪除")
                else:
                    del_edge_str = st.selectbox("選擇關係", options=edge_options, key="del_edge")
                    if st.button("確認刪除", type="primary", width="stretch"):
                        u, v = del_edge_str.split(" -> ")
                        success, msg = st.session_state['manager'].delete_relationship(st.session_state['graph'], u, v)
                        if success: st.toast(msg, icon="🗑️"); st.rerun()
                        else: st.error(msg)

        with st.expander("✏️ 修改資料", expanded=False):
            edit_type = st.radio("欲修改的項目", ["角色描述", "關係標籤"], horizontal=True)
            if edit_type == "角色描述":
                edit_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="edit_node")
                current_desc = st.session_state['graph'].nodes[edit_node].get('title', '')
                new_desc = st.text_area("更新描述", value=current_desc)
                if st.button("更新", width="stretch"):
                    success, msg = st.session_state['manager'].edit_character_description(st.session_state['graph'], edit_node, new_desc)
                    if success: st.toast(msg, icon="✏️"); st.rerun()
                    else: st.error(msg)
            elif edit_type == "關係標籤":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options: st.info("無關係可修改")
                else:
                    edit_edge_str = st.selectbox("選擇關係", options=edge_options, key="edit_edge")
                    u, v = edit_edge_str.split(" -> ")
                    current_label = st.session_state['graph'][u][v].get('label', '')
                    new_label = st.text_input("更新關係類型", value=current_label)
                    if st.button("更新", width="stretch"):
                        success, msg = st.session_state['manager'].edit_relationship_label(st.session_state['graph'], u, v, new_label)
                        if success: st.toast(msg, icon="✏️"); st.rerun()
                        else: st.error(msg)

with col_right:
    st.subheader("📊 知識圖譜視覺化")
    graph = st.session_state['graph']
    
    final_graph = graph
    if 'search_target' not in locals(): search_target = "(顯示全部)"
    if search_target != "(顯示全部)":
        target = search_target
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

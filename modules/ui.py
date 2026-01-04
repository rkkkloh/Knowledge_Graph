import streamlit as st
import streamlit.components.v1 as components

def render_sidebar():
    with st.sidebar:
        st.header("🎛️ 專案控制台")

        # --- API 設定 ---
        st.header("API 設定")
        st.info("尚未擁有 Key？點擊下方按鈕免費產生：")
        st.link_button("產生 Groq API Key (免費)", "https://console.groq.com/keys")
        
        if 'api_key' not in st.session_state:
            st.session_state['api_key'] = ""
            
        api_key_input = st.text_input(
            "輸入 API Key (貼上 gsk_...)", 
            type="password", 
            placeholder="gsk_...", 
            value=st.session_state['api_key']
        )
        st.session_state['api_key'] = api_key_input
        
        if api_key_input:
            st.caption("✅ 已輸入 Key")
        else:
            st.warning("⚠️ 請輸入 Key 以啟用 AI 功能")
        
        st.markdown("---")
        
        # Undo / Redo 控制區
        c1, c2 = st.columns(2)
        with c1:
            if st.button("↩️ Undo", use_container_width=True):
                new_graph, msg = st.session_state['manager'].undo()
                if new_graph:
                    st.session_state['graph'] = new_graph
                    st.toast(msg)
                    st.rerun()
                else:
                    st.toast(msg, icon="⚠️")
        with c2:
            if st.button("↪️ Redo", use_container_width=True):
                new_graph, msg = st.session_state['manager'].redo()
                if new_graph:
                    st.session_state['graph'] = new_graph
                    st.toast(msg)
                    st.rerun()
                else:
                    st.toast(msg, icon="⚠️")

        # 鍵盤監聽：Ctrl+Z / Cmd+Z
        # 綁定到 window.parent.document 確保捕捉範圍涵蓋整個瀏覽器視窗
        components.html(
            """
            <script>
            (function() {
                const doc = window.parent.document;
                doc.addEventListener('keydown', function(e) {
                    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
                        e.preventDefault();
                        
                        // 重新抓取 DOM 元件，避免 Stale Element Reference
                        let buttons = Array.from(doc.querySelectorAll('button'));
                        
                        if (e.shiftKey) {
                            let btn = buttons.find(b => b.innerText.includes("Redo"));
                            if (btn) btn.click();
                        } else {
                            let btn = buttons.find(b => b.innerText.includes("Undo"));
                            if (btn) btn.click();
                        }
                    }
                });
            })();
            </script>
            """,
            height=0,
        )

        st.markdown("---")
        
        with st.expander("💾 專案管理", expanded=True):
            col_save_1, col_save_2 = st.columns([2, 1])
            with col_save_1:
                project_name = st.text_input("專案檔名", value="my_story", label_visibility="collapsed")
            with col_save_2:
                if st.button("Save", width='stretch'): 
                    success, msg = st.session_state['manager'].save_graph(st.session_state['graph'], project_name)
                    if success: st.toast(msg, icon="💾")
                    else: st.error(msg)

        st.markdown("---")
        st.header("👀 檢視設定")
        
        all_nodes = list(st.session_state['graph'].nodes())
        st.session_state['search_target'] = st.selectbox("🔍 搜尋並聚焦角色", ["(顯示全部)"] + all_nodes)
        
        if st.button("⚠️ Reset", type="primary", use_container_width=True):
            success, msg = st.session_state['manager'].reset_graph(st.session_state['graph'])
            
            # 清除 JS 記憶並重新載入頁面
            clear_js = """
            <script>
                localStorage.removeItem("nexus_graph_positions");
                localStorage.removeItem("nexus_graph_camera");
                window.parent.location.reload();
            </script>
            """
            components.html(clear_js, height=0)
            
        st.markdown("---")

        st.subheader("🏆 關鍵角色 Top 5")
        
        if hasattr(st.session_state['manager'], 'analyze_centrality'):
            if st.session_state['graph'].number_of_nodes() > 0:
                top_nodes = st.session_state['manager'].analyze_centrality(st.session_state['graph'])
                for rank, (name, score) in enumerate(top_nodes, 1):
                    st.write(f"**#{rank} {name}**")
                    st.progress(score) 
            else:
                st.caption("尚無資料")
        else:
            st.caption("請更新 backend.py 啟用分析功能")
            
        st.markdown("---")
        
        uploaded_file = st.file_uploader("選擇 JSON 檔案", type="json", label_visibility="collapsed")
        if uploaded_file is not None:
            if st.button("Load Project", width='stretch'):
                new_graph, msg = st.session_state['manager'].load_graph(uploaded_file)
                if new_graph:
                    st.session_state['graph'] = new_graph
                    components.html("<script>localStorage.removeItem('nexus_graph_positions'); window.parent.location.reload();</script>", height=0)
                    st.toast(msg, icon="📂")
                else:
                    st.error(msg)
    
        st.caption("Designed by Loh Rui Kang")

def render_main_tabs():
    tab_char, tab_rel, tab_ai, tab_manage = st.tabs(["👤 新增", "🔗 連結", "🤖 AI", "⚙️ 管理"])
    
    # 新增角色
    with tab_char:
        with st.form("char_form", clear_on_submit=True):
            c_name = st.text_input("角色名稱 (必填)", placeholder="例如：哈利波特")
            c_desc = st.text_area("角色描述", placeholder="例如：葛來分多的學生...")
            if st.form_submit_button("✨ 加入角色", width='stretch'):
                if not c_name: st.error("❌ 請輸入角色名稱！")
                else:
                    success, msg = st.session_state['manager'].add_character(
                        st.session_state['graph'], c_name, c_desc
                    )
                    if success: st.toast(msg, icon="✅")
                    else: st.error(msg)

    # 建立連結
    with tab_rel:
        with st.form("rel_form", clear_on_submit=True):
            current_nodes = list(st.session_state['graph'].nodes())
            c1, c2 = st.columns(2)
            with c1: source = st.selectbox("來源角色", options=current_nodes, key="src_select")
            with c2: target = st.selectbox("目標角色", options=current_nodes, key="tgt_select")
            relation = st.text_input("關係類型", placeholder="例如：朋友、敵人")
            
            if st.form_submit_button("🔗 建立連結", width='stretch'):
                if source == target: st.warning("⚠️ 來源與目標不能是同一個人！")
                elif not relation: st.error("❌ 請輸入關係類型！")
                else:
                    success, msg = st.session_state['manager'].add_relationship(
                        st.session_state['graph'], source, target, relation
                    )
                    if success: st.toast(msg, icon="🔗")
                    else: st.error(msg)

    # AI 分析
    with tab_ai:
        st.caption("支援 OpenAI 與 Groq")
        source_text = st.text_area("故事文本", height=150, placeholder="請貼上一段小說內容...")
        
        api_key = st.session_state.get('api_key', '')

        if st.button("🚀 開始分析", width='stretch'):
            if not source_text: st.warning("⚠️ 請先貼上文章內容！")
            elif not api_key: st.error("❌ 尚未設定 API Key！")
            else:
                with st.spinner("🤖 AI 正在分析關係..."):
                    ai_nodes, ai_edges, error = st.session_state['manager'].process_text_with_ai(source_text, api_key)
                    
                    if not ai_nodes and not ai_edges and not error:
                        st.warning("🤔 AI 未發現內容。")
                    elif error: 
                        st.error(f"AI 呼叫失敗：{error}")
                    else:
                        st.session_state['ai_result'] = {"nodes": ai_nodes, "edges": ai_edges}
                        st.toast("分析完成！", icon="✅")

        if 'ai_result' in st.session_state:
            res = st.session_state['ai_result']
            st.divider()
            st.markdown("#### 🕵️ 審核結果")
            st.dataframe(res['nodes'], width='stretch')
            st.dataframe(res['edges'], width='stretch')
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ 確認匯入", type="primary", width='stretch', key="btn_confirm_ai"):
                    msg = st.session_state['manager'].batch_import(st.session_state['graph'], res['nodes'], res['edges'])
                    st.toast(msg, icon="✅")
                    del st.session_state['ai_result']
                    st.rerun()
            with b2:
                if st.button("🗑️ 放棄", width='stretch', key="btn_cancel_ai"):
                    del st.session_state['ai_result']
                    st.rerun()

    # 管理功能
    with tab_manage:
        with st.expander("🗑️ 刪除資料", expanded=True):
            del_type = st.radio("欲刪除的項目", ["角色", "關係"], horizontal=True)
            if del_type == "角色":
                del_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="del_node")
                if st.button("確認刪除", type="primary", width='stretch'):
                    success, msg = st.session_state['manager'].delete_character(st.session_state['graph'], del_node)
                    if success: st.toast(msg, icon="🗑️"); st.rerun()
                    else: st.error(msg)
            elif del_type == "關係":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options: st.info("無關係可刪除")
                else:
                    del_edge_str = st.selectbox("選擇關係", options=edge_options, key="del_edge")
                    if st.button("確認刪除", type="primary", width='stretch'):
                        u, v = del_edge_str.split(" -> ")
                        success, msg = st.session_state['manager'].delete_relationship(st.session_state['graph'], u, v)
                        if success: st.toast(msg, icon="🗑️"); st.rerun()
                        else: st.error(msg)

        with st.expander("✏️ 修改資料", expanded=False):
            edit_type = st.radio("欲修改的項目", ["角色描述", "關係標籤"], horizontal=True)
            if edit_type == "角色描述":
                edit_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="edit_node")
                current_desc = ""
                if st.session_state['graph'].has_node(edit_node):
                    current_desc = st.session_state['graph'].nodes[edit_node].get('title', '')
                
                new_desc = st.text_area("更新描述", value=current_desc)
                if st.button("更新", width='stretch'):
                    success, msg = st.session_state['manager'].edit_character_description(st.session_state['graph'], edit_node, new_desc)
                    if success: st.toast(msg, icon="✏️"); st.rerun()
                    else: st.error(msg)
            elif edit_type == "關係標籤":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options: st.info("無關係可修改")
                else:
                    edit_edge_str = st.selectbox("選擇關係", options=edge_options, key="edit_edge")
                    u, v = edit_edge_str.split(" -> ")
                    
                    current_label = ""
                    if st.session_state['graph'].has_edge(u, v):
                        current_label = st.session_state['graph'][u][v].get('label', '')
                        
                    new_label = st.text_input("更新關係類型", value=current_label)
                    if st.button("更新", width='stretch'):
                        success, msg = st.session_state['manager'].edit_relationship_label(st.session_state['graph'], u, v, new_label)
                        if success: st.toast(msg, icon="✏️"); st.rerun()
                        else: st.error(msg)
import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os
import json
import random
from modules.backend import GraphManager

# 設定頁面配置
st.set_page_config(
    page_title="Nexus Graph | 互動式知識圖譜",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_interactive_graph(nx_graph):
    """
    產生 PyVis 圖表並注入 JS，解決 Streamlit 每次 rerender 都會重置視角的問題。
    功能：記憶位置 (LocalStorage)、記憶縮放、新節點生在視野中心。
    """
    # 初始化 PyVis (深色主題)
    net = Network(height="700px", width="100%", bgcolor="#222831", font_color="white", directed=True)
    net.from_nx(nx_graph)
    
    # 視覺與物理參數設定
    options = {
        "nodes": {
            "borderWidth": 2,
            "color": { "highlight": { "border": "#00ADB5", "background": "#393E46" } },
            "shape": "dot",
            "size": 30,
            "font": { 
                "size": 24, "face": "tahoma", "color": "white",
                "strokeWidth": 5, "strokeColor": "#222831"
            },
            "scaling": {
                "min": 20, "max": 60,
                "label": { "enabled": True, "min": 14, "max": 40 }
            }
        },
        "edges": {
            "arrows": { "to": { "enabled": True, "scaleFactor": 1.0 } },
            "color": { "inherit": True, "opacity": 0.6 },
            "font": {
                "size": 16, "color": "#00ADB5", "background": "#222831",
                "strokeWidth": 0, "align": "middle",
            },
            "smooth": { "type": "dynamic" }
        },
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -3000, 
                "centralGravity": 0.1,            
                "springLength": 150,              
                "springConstant": 0.05,
                "damping": 0.9,
                "avoidOverlap": 1
            },
            "minVelocity": 0.55,
            "solver": "barnesHut",
            "stabilization": { "enabled": False } # 關閉預計算以加速載入
        },
        "interaction": {
            "dragNodes": True, "dragView": True, "zoomView": True, "hover": True
        }
    }
    
    net.set_options(f"var options = {json.dumps(options)}")
    html_data = net.generate_html()

    # JS 注入：處理位置記憶與視角恢復
    js_injection = """
    <script type="text/javascript">
        var isFirstLoad = true;

        network.on("afterDrawing", function (ctx) {
            if (!isFirstLoad) return;
            isFirstLoad = false;

            // 嘗試從 LocalStorage 恢復節點座標
            var savedPositions = localStorage.getItem("nexus_graph_positions");
            var currentNodes = nodes.getIds();
            var existingNodeIds = new Set();

            if (savedPositions) {
                var positions = JSON.parse(savedPositions);
                currentNodes.forEach(function(nodeId) {
                    if (positions[nodeId]) {
                        network.body.nodes[nodeId].x = positions[nodeId].x;
                        network.body.nodes[nodeId].y = positions[nodeId].y;
                        existingNodeIds.add(nodeId);
                    }
                });
            }

            // 恢復鏡頭縮放狀態
            var savedCamera = localStorage.getItem("nexus_graph_camera");
            if (savedCamera) {
                var cameraState = JSON.parse(savedCamera);
                network.moveTo({
                    position: cameraState.position,
                    scale: cameraState.scale,
                    animation: false
                });
                
                // 讓新節點出生在目前的視野中心，而不是隨機亂飄
                var centerPos = network.getViewPosition();
                currentNodes.forEach(function(nodeId) {
                    if (!existingNodeIds.has(nodeId)) {
                        var offsetX = (Math.random() - 0.5) * 100;
                        var offsetY = (Math.random() - 0.5) * 100;
                        network.moveNode(nodeId, centerPos.x + offsetX, centerPos.y + offsetY);
                    }
                });
            } else {
                network.fit({animation: false}); 
            }
            network.startSimulation();
        });

        // 事件監聽：拖曳或縮放時存檔
        network.on("dragEnd", function (params) {
            if (params.nodes.length > 0) saveNodePositions();
            saveCameraState();
        });
        
        network.on("zoom", function() { saveCameraState(); });
        network.on("dragView", function() { saveCameraState(); });
        network.on("stabilizationIterationsDone", function() { saveNodePositions(); });

        function saveNodePositions() {
            var allPositions = network.getPositions();
            var oldData = localStorage.getItem("nexus_graph_positions");
            var savedData = oldData ? JSON.parse(oldData) : {};
            for (var nodeId in allPositions) {
                savedData[nodeId] = allPositions[nodeId];
            }
            localStorage.setItem("nexus_graph_positions", JSON.stringify(savedData));
        }

        function saveCameraState() {
            var scale = network.getScale();
            var position = network.getViewPosition();
            var cameraState = { scale: scale, position: position };
            localStorage.setItem("nexus_graph_camera", JSON.stringify(cameraState));
        }

        // 雙擊空白處 Reset 視角
        network.on("doubleClick", function(params) {
             if (params.nodes.length === 0) {
                network.fit({animation: true});
                setTimeout(saveCameraState, 1000);
             }
        });
    </script>
    """
    
    html_data = html_data.replace('</body>', f'{js_injection}</body>')
    components.html(html_data, height=710, scrolling=False)

    # 匯出 HTML 功能
    st.caption("💡 提示：雙擊空白處可自動置中 (Fit)")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, "rb") as f:
            html_bytes = f.read()
        st.download_button(
            label="🌏 下載此圖表 (HTML)",
            data=html_bytes,
            file_name="knowledge_graph.html",
            mime="text/html",
        )
        os.unlink(tmp.name)

# --- Main App Logic ---

# 初始化 State
if 'graph' not in st.session_state:
    manager = GraphManager()
    st.session_state['graph'] = manager.get_initial_graph()
    st.session_state['manager'] = manager
    # 清除舊的位置快取，避免 ID 衝突
    if 'node_positions' in st.session_state:
        del st.session_state['node_positions']

st.title("🕸️ Nexus Graph 知識圖譜編輯器")
st.markdown("---")

# --- Sidebar ---
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
    
    # 存檔區塊
    with st.expander("💾 專案管理", expanded=True):
        col_save_1, col_save_2 = st.columns([2, 1])
        with col_save_1:
            project_name = st.text_input("專案檔名", value="my_story", label_visibility="collapsed")
        with col_save_2:
            if st.button("Save", use_container_width=True): 
                success, msg = st.session_state['manager'].save_graph(st.session_state['graph'], project_name)
                if success: st.toast(msg, icon="💾")
                else: st.error(msg)

        st.markdown("---")
        st.header("👀 檢視設定")
        
        all_nodes = list(st.session_state['graph'].nodes())
        search_target = st.selectbox("🔍 搜尋並聚焦角色", ["(顯示全部)"] + all_nodes)
        
        # 強制重置按鈕 (透過 JS 清除 LocalStorage)
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
        
        # 讀檔
        uploaded_file = st.file_uploader("選擇 JSON 檔案", type="json", label_visibility="collapsed")
        if uploaded_file is not None:
            if st.button("Load Project", use_container_width=True):
                new_graph, msg = st.session_state['manager'].load_graph(uploaded_file)
                if new_graph:
                    st.session_state['graph'] = new_graph
                    # 讀檔時一併清除舊記憶
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

# --- Main Layout ---
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("📝 編輯資料")
    tab_char, tab_rel, tab_ai, tab_manage = st.tabs(["👤 新增", "🔗 連結", "🤖 AI", "⚙️ 管理"])
    
    # Tab 1: Manual Add Character
    with tab_char:
        with st.form("char_form", clear_on_submit=True):
            c_name = st.text_input("角色名稱 (必填)", placeholder="例如：哈利波特")
            c_desc = st.text_area("角色描述", placeholder="例如：葛來分多的學生...")
            if st.form_submit_button("✨ 加入角色", use_container_width=True):
                if not c_name: st.error("❌ 請輸入角色名稱！")
                else:
                    success, msg = st.session_state['manager'].add_character(
                        st.session_state['graph'], c_name, c_desc
                    )
                    if success: st.toast(msg, icon="✅")
                    else: st.error(msg)

    # Tab 2: Manual Add Relation
    with tab_rel:
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

    # Tab 3: AI Generation
    with tab_ai:
        st.caption("支援 OpenAI 與 Groq (貼上 Key 即可自動切換)")
        source_text = st.text_area("故事文本", height=150, placeholder="請貼上一段小說內容...")
        
        if st.button("🚀 開始分析", use_container_width=True):
            if not source_text: st.warning("⚠️ 請先貼上文章內容！")
            elif not api_key: st.error("❌ 尚未設定 API Key！")
            else:
                with st.spinner("🤖 AI 正在分析關係..."):
                    ai_nodes, ai_edges, error = st.session_state['manager'].process_text_with_ai(source_text, api_key)
                    
                    if not ai_nodes and not ai_edges and not error:
                        st.warning("🤔 AI 沒有找到任何角色或關係，請嘗試提供更完整的句子。")
                    elif error: 
                        st.error(f"AI 呼叫失敗：{error}")
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
                if st.button("✅ 確認匯入", type="primary", use_container_width=True, key="btn_confirm_ai"):
                    msg = st.session_state['manager'].batch_import(st.session_state['graph'], res['nodes'], res['edges'])
                    st.toast(msg, icon="✅")
                    del st.session_state['ai_result']
                    st.rerun()
            with b2:
                if st.button("🗑️ 放棄", use_container_width=True, key="btn_cancel_ai"):
                    del st.session_state['ai_result']
                    st.rerun()
            with b2:
                if st.button("🗑️ 放棄", use_container_width=True):
                    del st.session_state['ai_result']
                    st.rerun()

    # Tab 4: Delete / Edit
    with tab_manage:
        with st.expander("🗑️ 刪除資料", expanded=True):
            del_type = st.radio("欲刪除的項目", ["角色", "關係"], horizontal=True)
            if del_type == "角色":
                del_node = st.selectbox("選擇角色", options=list(st.session_state['graph'].nodes()), key="del_node")
                if st.button("確認刪除", type="primary", use_container_width=True):
                    success, msg = st.session_state['manager'].delete_character(st.session_state['graph'], del_node)
                    if success: st.toast(msg, icon="🗑️"); st.rerun()
                    else: st.error(msg)
            elif del_type == "關係":
                edge_options = [f"{u} -> {v}" for u, v in st.session_state['graph'].edges()]
                if not edge_options: st.info("無關係可刪除")
                else:
                    del_edge_str = st.selectbox("選擇關係", options=edge_options, key="del_edge")
                    if st.button("確認刪除", type="primary", use_container_width=True):
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
                if st.button("更新", use_container_width=True):
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
                    if st.button("更新", use_container_width=True):
                        success, msg = st.session_state['manager'].edit_relationship_label(st.session_state['graph'], u, v, new_label)
                        if success: st.toast(msg, icon="✏️"); st.rerun()
                        else: st.error(msg)

with col_right:
    st.subheader("📊 知識圖譜視覺化")
    graph = st.session_state['graph']
    
    # 處理搜尋聚焦邏輯
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

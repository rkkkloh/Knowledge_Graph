import streamlit as st
import networkx as nx
from modules.backend import GraphManager
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os
import json
import random

# 設定頁面配置
st.set_page_config(
    page_title="Nexus Graph | 互動式知識圖譜",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

<<<<<<< Updated upstream
# --- 輔助函式：繪製 PyVis 圖表 ---
=======
# --- 繪圖核心：處理 PyVis 參數與 JavaScript 注入 ---
>>>>>>> Stashed changes
def render_interactive_graph(nx_graph):
    """
    繪製互動式圖表。
    包含 JS 注入以實現：位置記憶 (LocalStorage)、鏡頭狀態保存、以及新節點的智慧出生點。
    """
<<<<<<< Updated upstream
    # 1. 建立 PyVis 网络物件
    # height 設定畫布高度，bgcolor 設定背景色配合深色主題
    net = Network(height="600px", width="100%", bgcolor="#222831", font_color="white")
    
    # 2. 載入 NetworkX 資料
    net.from_nx(nx_graph)
    
    # 3. 設置物理引擎與樣式 (這是讓圖漂亮的關鍵)
    # 我們使用 'force_atlas_2based' 演算法，這是最適合展示知識圖譜的物理模型
    net.set_options("""
    var options = {
=======
    # 初始化 PyVis，使用深色背景
    net = Network(height="700px", width="100%", bgcolor="#222831", font_color="white", directed=True)
    net.from_nx(nx_graph)
    
    # 設定物理引擎與視覺樣式
    options = {
>>>>>>> Stashed changes
      "nodes": {
        "borderWidth": 2,
        "color": { "highlight": { "border": "#00ADB5", "background": "#393E46" } },
        "shape": "dot",
        "size": 30,
        "font": { 
            "size": 24,
            "face": "tahoma",
            "color": "white",
            "strokeWidth": 5, # 加粗描邊避免背景干擾文字
            "strokeColor": "#222831"
        },
<<<<<<< Updated upstream
        "font": {
          "size": 16,
          "face": "tahoma"
        }
      },
      "edges": {
        "color": {
          "inherit": true
        },
        "smooth": false
=======
        "scaling": {
            "min": 20, "max": 60,
            "label": { "enabled": True, "min": 14, "max": 40 }
        }
      },
      "edges": {
        "arrows": { "to": { "enabled": True, "scaleFactor": 1.0 } },
        "color": { "inherit": True, "opacity": 0.6 },
        "font": {
            "size": 16,
            "color": "#00ADB5",      # 使用亮青色凸顯關係
            "background": "#222831", # 深色背景框，防止線條穿過文字
            "strokeWidth": 0,
            "align": "middle",
        },
        "smooth": { "type": "dynamic" }
>>>>>>> Stashed changes
      },
      "physics": {
        "enabled": True,
        "barnesHut": {
            "gravitationalConstant": -3000, 
            "centralGravity": 0.1,           
            "springLength": 150,             
            "springConstant": 0.05,
            "damping": 0.9,                  # 高阻尼，讓移動更平穩，減少閃爍
            "avoidOverlap": 1                # 強制防止節點重疊
        },
        "minVelocity": 0.05,
        "solver": "barnesHut",
        "stabilization": {
            "enabled": False                 # 關閉預計算，達到秒開效果
        }
      },
      "interaction": {
          "dragNodes": True,
          "dragView": True,
          "zoomView": True,
          "hover": True
      }
    }
<<<<<<< Updated upstream
    """)
    
    # 4. 生成 HTML 檔案 (使用暫存檔避免檔案權限問題)
    try:
        # 建立一個暫存檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.save_graph(tmp_file.name)
            # 讀取生成的 HTML 內容
            tmp_file.seek(0)
            html_content = tmp_file.read().decode('utf-8')
        
        # 5. 在 Streamlit 顯示
        components.html(html_content, height=610, scrolling=False)
        
        # 清理暫存檔
        os.unlink(tmp_file.name)
        
    except Exception as e:
        st.error(f"圖表繪製失敗: {e}")
=======
    
    net.set_options(f"var options = {json.dumps(options)}")
    html_data = net.generate_html()

    # --- JavaScript 注入區 ---
    # 負責處理：瀏覽器端的 LocalStorage 存取、鏡頭控制、以及節點初始位置計算
    js_injection = """
    <script type="text/javascript">
        var isFirstLoad = true;

        // 監聽：圖表繪製完成後觸發
        network.on("afterDrawing", function (ctx) {
            if (!isFirstLoad) return;
            isFirstLoad = false;

            // 1. 恢復節點位置
            var savedPositions = localStorage.getItem("nexus_graph_positions");
            var currentNodes = nodes.getIds();
            var existingNodeIds = new Set();

            if (savedPositions) {
                var positions = JSON.parse(savedPositions);
                currentNodes.forEach(function(nodeId) {
                    if (positions[nodeId]) {
                        // 如果是舊節點，移回記憶中的座標
                        network.body.nodes[nodeId].x = positions[nodeId].x;
                        network.body.nodes[nodeId].y = positions[nodeId].y;
                        existingNodeIds.add(nodeId);
                    }
                });
            }

            // 2. 恢復鏡頭狀態 (縮放與位移)
            var savedCamera = localStorage.getItem("nexus_graph_camera");
            
            if (savedCamera) {
                var cameraState = JSON.parse(savedCamera);
                network.moveTo({
                    position: cameraState.position,
                    scale: cameraState.scale,
                    animation: false
                });
                
                // 3. 處理新節點：讓它們出生在當前視角的中心
                var centerPos = network.getViewPosition();
                currentNodes.forEach(function(nodeId) {
                    if (!existingNodeIds.has(nodeId)) {
                        // 加一點隨機偏移，避免多個新節點重疊
                        var offsetX = (Math.random() - 0.5) * 100;
                        var offsetY = (Math.random() - 0.5) * 100;
                        network.moveNode(nodeId, centerPos.x + offsetX, centerPos.y + offsetY);
                    }
                });

            } else {
                // 如果完全沒有紀錄 (第一次使用)，自動調整視窗大小
                network.fit({animation: false}); 
            }
            
            // 強制啟動物理模擬
            network.startSimulation();
        });

        // --- 事件監聽器：隨時儲存狀態 ---
        
        network.on("dragEnd", function (params) {
            if (params.nodes.length > 0) saveNodePositions();
            saveCameraState();
        });
        
        network.on("zoom", function() { saveCameraState(); });
        network.on("dragView", function() { saveCameraState(); });
        
        // 當物理運動靜止時，也要存一次 (捕捉自動佈局的結果)
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

        // 雙擊空白處：重置鏡頭 (Fit)
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

    # 匯出 HTML 按鈕
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
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    st.info("目前模式：Mocking (模擬後端)")
=======
>>>>>>> Stashed changes

    st.header("🔑 API 設定")
    st.info("💡 尚未擁有 Key？點擊下方按鈕免費產生：")
    st.link_button("👉 產生 Groq API Key (免費)", "https://console.groq.com/keys")
    
    api_key = st.text_input("輸入 API Key (貼上 gsk_...)", type="password", placeholder="gsk_...")
    
    if api_key:
        st.caption("✅ 已輸入 Key")
    else:
        st.warning("⚠️ 請輸入 Key 以啟用 AI 功能")
    
    st.markdown("---")
    
<<<<<<< Updated upstream
    # 專案存檔區塊
    with st.expander("💾 專案管理 (Save/Load)", expanded=True):
        # 1. 存檔功能
        st.caption("儲存專案")
=======
    with st.expander("💾 專案管理", expanded=True):
>>>>>>> Stashed changes
        col_save_1, col_save_2 = st.columns([2, 1])
        with col_save_1:
            project_name = st.text_input("專案檔名", value="my_story", label_visibility="collapsed")
        with col_save_2:
            if st.button("Save", width="stretch"):
                success, msg = st.session_state['manager'].save_graph(st.session_state['graph'], project_name)
<<<<<<< Updated upstream
                if success:
                    st.toast(msg, icon="💾")
                else:
                    st.error(msg)
        
        st.markdown("---")
        
        # 2. 讀檔功能 (新增的部分)
        st.caption("載入舊專案")
=======
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
        
>>>>>>> Stashed changes
        uploaded_file = st.file_uploader("選擇 JSON 檔案", type="json", label_visibility="collapsed")
        if uploaded_file is not None:
<<<<<<< Updated upstream
            # 避免重複載入，可以檢查 session state 或直接執行
            if st.button("Load Project", use_container_width=True):
=======
            if st.button("Load Project", width="stretch"):
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
                    st.rerun() # 重新整理頁面以顯示新圖
=======
>>>>>>> Stashed changes
                else:
                    st.error(msg)
    
    st.caption("Designed by Group B")

# 5. 主畫面佈局
col_left, col_right = st.columns([1, 2], gap="large")

<<<<<<< Updated upstream
# === 左側：編輯區 (您的核心工作) ===
with col_left:
    st.subheader("📝 編輯資料")
    
    # 【修改點 1】這裡改成三個 Tabs
    tab_char, tab_rel, tab_ai = st.tabs(["👤 新增角色", "🔗 建立關係", "🤖 AI 智慧萃取"])
    
    # --- Tab 1: 角色表單 ---
=======
with col_left:
    st.subheader("📝 編輯資料")
    tab_char, tab_rel, tab_ai, tab_manage = st.tabs(["👤 新增", "🔗 連結", "🤖 AI", "⚙️ 管理"])
    
    # Tab 1: 新增角色
>>>>>>> Stashed changes
    with tab_char:
        with st.form("char_form", clear_on_submit=True):
            c_name = st.text_input("角色名稱 (必填)", placeholder="例如：哈利波特")
            c_desc = st.text_area("角色描述", placeholder="例如：葛來分多的學生...")
<<<<<<< Updated upstream
            
            # 送出按鈕
            submitted = st.form_submit_button("✨ 加入角色", use_container_width=True)
            
            if submitted:
                if not c_name:
                    st.error("❌ 請輸入角色名稱！")
=======
            if st.form_submit_button("✨ 加入角色", width="stretch"):
                if not c_name: st.error("❌ 請輸入角色名稱！")
>>>>>>> Stashed changes
                else:
                    # 呼叫後端
                    success, msg = st.session_state['manager'].add_character(
                        st.session_state['graph'], c_name, c_desc
                    )
                    if success:
                        st.toast(msg, icon="✅") # 使用 Toast 彈出式訊息，更現代
                    else:
                        st.error(msg)

<<<<<<< Updated upstream
    # --- Tab 2: 關係表單 ---
=======
    # Tab 2: 建立連結
>>>>>>> Stashed changes
    with tab_rel:
        with st.form("rel_form", clear_on_submit=True):
            # 獲取目前所有角色清單 (給使用者選，防止打錯字)
            current_nodes = list(st.session_state['graph'].nodes())
            
<<<<<<< Updated upstream
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
=======
            if st.form_submit_button("🔗 建立連結", width="stretch"):
                if source == target: st.warning("⚠️ 來源與目標不能是同一個人！")
                elif not relation: st.error("❌ 請輸入關係類型！")
>>>>>>> Stashed changes
                else:
                    success, msg = st.session_state['manager'].add_relationship(
                        st.session_state['graph'], source, target, relation
                    )
                    if success:
                        st.toast(msg, icon="🔗")
                    else:
                        st.error(msg)

<<<<<<< Updated upstream
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
=======
    # Tab 3: AI 分析
    with tab_ai:
        st.caption("支援 OpenAI 與 Groq (貼上 Key 即可自動切換)")
        source_text = st.text_area("故事文本", height=150, placeholder="請貼上一段小說內容...")
        
        if st.button("🚀 開始分析", width="stretch"):
            if not source_text: st.warning("⚠️ 請先貼上文章內容！")
            elif not api_key: st.error("❌ 尚未設定 API Key！")
>>>>>>> Stashed changes
            else:
                with st.spinner("🤖 AI 正在閱讀故事並分析關係 (這可能需要幾秒鐘)..."):
                    # 呼叫真實的後端函式
                    ai_nodes, ai_edges, error = st.session_state['manager'].process_text_with_ai(source_text, api_key)
                    
<<<<<<< Updated upstream
                    if error:
=======
                    # 處理 AI 回傳空值的情況 (例如輸入無意義字串)
                    if not ai_nodes and not ai_edges and not error:
                        st.warning("🤔 AI 沒有在文本中找到任何角色或關係。請嘗試輸入更完整的句子。")
                    elif error: 
>>>>>>> Stashed changes
                        st.error(f"AI 呼叫失敗：{error}")
                    else:
                        # 將結果暫存在 session_state
                        st.session_state['ai_result'] = {"nodes": ai_nodes, "edges": ai_edges}
                        st.toast("分析完成！請往下確認結果", icon="✅")

        # 2. 結果審核區 (如果有分析結果才顯示)
        if 'ai_result' in st.session_state:
            res = st.session_state['ai_result']
            
            st.divider()
<<<<<<< Updated upstream
            st.markdown("#### 🕵️ 審核分析結果")
            
            # 顯示預覽表格 (使用 dataframe 比較美觀)
            st.markdown("**發現的角色：**")
=======
            st.markdown("#### 🕵️ 審核結果")
            # 顯示預覽表格
>>>>>>> Stashed changes
            st.dataframe(res['nodes'], use_container_width=True)
            
            st.markdown("**發現的關係：**")
            st.dataframe(res['edges'], use_container_width=True)
            
<<<<<<< Updated upstream
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
=======
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

    # Tab 4: 資料管理
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
>>>>>>> Stashed changes

with col_right:
    st.subheader("📊 知識圖譜視覺化")
<<<<<<< Updated upstream
    
    # 顯示統計數據 (Metrics)
=======
>>>>>>> Stashed changes
    graph = st.session_state['graph']
    
<<<<<<< Updated upstream
    # 這些卡片顯示在圖的上方
    c1, c2, c3 = st.columns(3)
    c1.metric("角色", nodes_count, delta=f"+{nodes_count} (Total)")
    c2.metric("關係", edges_count, help="目前的連結總數")
    
    # 計算密度 (這是一個專業的圖學指標，代表圖的複雜度)
    density = nx.density(graph)
    c3.metric("圖譜密度", f"{density:.3f}", help="數值越高代表關係越緊密")
    
    st.markdown("---")
    
    # 呼叫我們剛剛寫的視覺化函式
    if nodes_count > 0:
        with st.spinner("正在運算物理佈局..."):
            render_interactive_graph(graph)
=======
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
>>>>>>> Stashed changes
    else:
        st.info("目前沒有資料，請在左側新增角色來開始！")
    
<<<<<<< Updated upstream
    # 額外功能：顯示圖例或說明
    with st.expander("ℹ️ 操作說明"):
        st.markdown("""
        - **縮放**：使用滑鼠滾輪
        - **移動**：點擊空白處拖曳
        - **選取**：點擊角色可高亮顯示
        - **調整**：您可以拖曳節點來改變位置
        """)
=======
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("角色總數", graph.number_of_nodes())
    c2.metric("關係總數", graph.number_of_edges())
    c3.metric("密度", f"{nx.density(graph):.3f}")
>>>>>>> Stashed changes

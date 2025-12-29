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
def render_interactive_graph(nx_graph):
    """
    將 NetworkX 圖轉換為 PyVis HTML 並在 Streamlit 中顯示
    """
    # 1. 建立 PyVis 网络物件
    # height 設定畫布高度，bgcolor 設定背景色配合深色主題
    net = Network(height="600px", width="100%", bgcolor="#222831", font_color="white")
    
    # 2. 載入 NetworkX 資料
    net.from_nx(nx_graph)
    
    # 3. 設置物理引擎與樣式 (這是讓圖漂亮的關鍵)
    # 我們使用 'force_atlas_2based' 演算法，這是最適合展示知識圖譜的物理模型
    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 2,
        "color": {
          "highlight": {
            "border": "#00ADB5",
            "background": "#393E46"
          }
        },
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
    
    # 【修改點 1】這裡改成三個 Tabs
    tab_char, tab_rel, tab_ai = st.tabs(["👤 新增角色", "🔗 建立關係", "🤖 AI 智慧萃取"])
    
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
    
    # 計算密度 (這是一個專業的圖學指標，代表圖的複雜度)
    density = nx.density(graph)
    c3.metric("圖譜密度", f"{density:.3f}", help="數值越高代表關係越緊密")
    
    st.markdown("---")
    
    # 呼叫我們剛剛寫的視覺化函式
    if nodes_count > 0:
        with st.spinner("正在運算物理佈局..."):
            render_interactive_graph(graph)
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
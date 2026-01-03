import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os
import json

def render_interactive_graph(nx_graph):
    """
    繪製互動式圖表。
    包含 JS 注入以實現：位置記憶 (LocalStorage)、鏡頭狀態保存、以及新節點的智慧出生點。
    """
    # 初始化 PyVis，使用深色背景
    net = Network(height="700px", width="100%", bgcolor="#222831", font_color="white", directed=True)
    net.from_nx(nx_graph)
    
    # 設定物理引擎與視覺樣式
    options = {
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
    
    net.set_options(f"var options = {json.dumps(options)}")
    
    # 生成 HTML 字串 (不直接存檔，而是先生成字串以便注入 JS)
    try:
        # PyVis 的 generate_html 會回傳完整 HTML 字串
        html_data = net.generate_html()
    except AttributeError:
        # 舊版 PyVis 可能沒有 generate_html，改用暫存檔讀取
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            with open(tmp.name, "r", encoding="utf-8") as f:
                html_data = f.read()
            os.unlink(tmp.name)

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
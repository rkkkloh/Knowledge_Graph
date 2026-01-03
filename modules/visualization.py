import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os
import json

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
    
    # 生成 HTML (相容性處理)
    try:
        html_data = net.generate_html()
    except AttributeError:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            with open(tmp.name, "r", encoding="utf-8") as f:
                html_data = f.read()
            os.unlink(tmp.name)

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
        
        # 加上 key 避免 ID 衝突
        st.download_button(
            label="🌏 下載此圖表 (HTML)",
            data=html_bytes,
            file_name="knowledge_graph.html",
            mime="text/html",
            key="download_graph_html" 
        )
        os.unlink(tmp.name)
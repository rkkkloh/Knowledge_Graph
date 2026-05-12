import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os
import json

def render_interactive_graph(nx_graph):
    """
    產生 PyVis 圖表並注入 JS。
    """
    # 初始化 PyVis
    net = Network(height="700px", width="100%", bgcolor="#222831", font_color="white", directed=True)
    net.from_nx(nx_graph)
    
    # 參數設定
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
            # [關鍵修正]：將 inherit 改為 False，這樣紅色跟綠色的線條才顯示得出來！
            "color": { "inherit": False, "opacity": 0.8 },
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
            "stabilization": { 
                "enabled": False,  
                "iterations": 0
            } 
        },
        "interaction": {
            "dragNodes": True, "dragView": True, "zoomView": True, "hover": True
        }
    }
    
    net.set_options(f"var options = {json.dumps(options)}")
    
    # 生成 HTML
    try:
        html_data = net.generate_html()
    except AttributeError:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            with open(tmp.name, "r", encoding="utf-8") as f:
                html_data = f.read()
            os.unlink(tmp.name)

    # JS 注入 (完全不變，保留您原本的拖曳記憶功能)
    js_injection = """
    <script type="text/javascript">
        var isFirstLoad = true;

        network.on("afterDrawing", function (ctx) {
            if (!isFirstLoad) return;
            isFirstLoad = false;

            // 1. 恢復座標
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
            } else {
                var center = network.getViewPosition();
                currentNodes.forEach(function(nodeId) {
                     var off = (Math.random() - 0.5) * 20; 
                     network.moveNode(nodeId, center.x + off, center.y + off);
                });
            }

            // 2. 恢復鏡頭
            var savedCamera = localStorage.getItem("nexus_graph_camera");
            if (savedCamera) {
                var cameraState = JSON.parse(savedCamera);
                network.moveTo({
                    position: cameraState.position,
                    scale: cameraState.scale,
                    animation: false
                });
                
                var centerPos = network.getViewPosition();
                currentNodes.forEach(function(nodeId) {
                    if (!existingNodeIds.has(nodeId)) {
                        var offsetX = (Math.random() - 0.5) * 50;
                        var offsetY = (Math.random() - 0.5) * 50;
                        network.moveNode(nodeId, centerPos.x + offsetX, centerPos.y + offsetY);
                    }
                });
            } else {
                network.fit({animation: false}); 
            }
            
            saveNodePositions();

            setTimeout(function() {
                network.startSimulation();
            }, 100);

            setTimeout(function() {
                saveNodePositions();
            }, 3000);
        });

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
            key="download_graph_html" 
        )
        os.unlink(tmp.name)
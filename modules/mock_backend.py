import networkx as nx
import random

class GraphManager:
    def __init__(self):
        # 這裡之後會換成真的資料庫載入邏輯
        pass

    def get_initial_graph(self):
        """回傳一個測試用的預設圖譜，讓你開發時不至於看到空白畫面"""
        G = nx.Graph()
        # 預設一些哈利波特的數據讓畫面好看
        G.add_node("哈利波特", title="存活下來的男孩", type="character", group=1)
        G.add_node("榮恩", title="哈利的好友", type="character", group=1)
        G.add_node("妙麗", title="萬事通", type="character", group=1)
        G.add_node("鄧不利多", title="校長", type="character", group=2)
        G.add_edge("哈利波特", "榮恩", label="摯友")
        G.add_edge("哈利波特", "妙麗", label="摯友")
        G.add_edge("哈利波特", "鄧不利多", label="師生")
        return G

    def add_character(self, graph, name, description):
        """模擬新增角色"""
        if graph.has_node(name):
            return False, f"⚠️ 角色 '{name}' 已經存在囉！"
        
        # 實際上這行不會真的存檔，因為這是 Mock，但會更新當下的 Graph 物件
        graph.add_node(name, title=description, type="character", group=1)
        return True, f"✅ 成功新增角色：{name}"

    def add_relationship(self, graph, source, target, relation):
        """模擬新增關係"""
        if graph.has_edge(source, target):
            return False, f"⚠️ '{source}' 和 '{target}' 之間已經有關係了。"
        
        graph.add_edge(source, target, label=relation)
        return True, f"🔗 成功連結：{source} --[{relation}]--> {target}"
    
    def save_graph(self, graph, filename):
        """模擬存檔"""
        return True, f"💾 專案 '{filename}' 已儲存 (模擬模式)"
    
    def simulate_ai_extraction(self, text):
        """
        模擬 AI 從文字中抓取資料的過程。
        回傳：(nodes列表, edges列表)
        """
        import time
        time.sleep(1.5) # 模擬 AI 思考的延遲時間
        
        # 這裡我們寫死一些假資料，假裝是從文字裡抓出來的
        # 實作真實 AI 時，這裡會換成 OpenAI API 的呼叫
        mock_nodes = [
            {"id": "馬份", "title": "史萊哲林學生", "type": "character"},
            {"id": "史內卜", "title": "魔藥學教授", "type": "character"}
        ]
        
        mock_edges = [
            {"source": "史內卜", "target": "馬份", "label": "偏袒"},
            {"source": "馬份", "target": "哈利波特", "label": "死對頭"}
        ]
        
        return mock_nodes, mock_edges

    def batch_import(self, graph, nodes, edges):
        """
        將 AI 分析確認後的資料，整批寫入圖譜
        """
        count_n = 0
        count_e = 0
        
        # 匯入節點
        for n in nodes:
            if not graph.has_node(n["id"]):
                graph.add_node(n["id"], **n) # **n 是把字典解包存進去
                count_n += 1
        
        # 匯入關係
        for e in edges:
            # 確保兩端節點都存在，不然會報錯 (防呆)
            if graph.has_node(e["source"]) and graph.has_node(e["target"]):
                # 檢查是否已存在同樣關係
                if not graph.has_edge(e["source"], e["target"]):
                    graph.add_edge(e["source"], e["target"], label=e["label"])
                    count_e += 1
                    
        return f"✅ 成功匯入 {count_n} 個新角色、{count_e} 條新關係！"
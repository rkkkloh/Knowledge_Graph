import networkx as nx
import json
import os
from openai import OpenAI

class GraphManager:
    def __init__(self):
        # 確保 data 資料夾存在
        if not os.path.exists('data'):
            os.makedirs('data')

    def get_initial_graph(self):
        """回傳一個空的或預設的圖"""
        G = nx.Graph()
        # 預設範例 (您可以選擇是否保留)
        G.add_node("哈利波特", title="存活下來的男孩", type="character", group=1)
        G.add_node("榮恩", title="哈利的好友", type="character", group=1)
        G.add_edge("哈利波特", "榮恩", label="摯友")
        return G

    def add_character(self, graph, name, description):
        if graph.has_node(name):
            return False, f"⚠️ Character '{name}' already exists."
        graph.add_node(name, title=description, type="character", group=1)
        return True, f"✅ Added character: {name}"

    def add_relationship(self, graph, source, target, relation):
        if graph.has_edge(source, target):
            return False, f"⚠️ Relationship between '{source}' and '{target}' already exists."
        graph.add_edge(source, target, label=relation)
        return True, f"🔗 Connected: {source} --[{relation}]--> {target}"
    
    # --- 真實的存檔邏輯 (Real Save) ---
    def save_graph(self, graph, filename):
        """將圖譜儲存為 JSON"""
        try:
            filepath = f"data/{filename}.json"
            # 將 NetworkX 物件轉為字典格式
            graph_data = nx.node_link_data(graph)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=4)
            
            return True, f"💾 Project saved to {filepath}"
        except Exception as e:
            return False, f"❌ Save failed: {str(e)}"

    # --- 真實的讀檔邏輯 (Real Load) ---
    def load_graph(self, uploaded_file):
        """從上傳的 JSON 檔案讀取圖譜"""
        try:
            # 讀取 JSON 資料
            graph_data = json.load(uploaded_file)
            # 轉換回 NetworkX 物件
            G = nx.node_link_graph(graph_data)
            return G, f"📂 Successfully loaded graph from {uploaded_file.name}"
        except Exception as e:
            return None, f"❌ Load failed: {str(e)}"

    # --- 真實 AI 處理邏輯 (Real AI) ---
    def process_text_with_ai(self, text, api_key):
        """
        呼叫 OpenAI API 進行實體關係萃取
        """
        client = OpenAI(api_key=api_key)
        
        # 這是給 AI 的指令 (Prompt Engineering)
        system_prompt = """
        你是一個知識圖譜專家。請從使用者的文本中萃取「實體(Character)」與「關係(Relationship)」。
        請務必回傳純 JSON 格式，不要包含 Markdown 標記或其他文字。
        格式如下：
        {
            "nodes": [{"id": "角色名", "title": "角色描述", "type": "character"}],
            "edges": [{"source": "角色名", "target": "角色名", "label": "關係類型"}]
        }
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o", # 或 gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}, # 強制回傳 JSON，超重要！
                temperature=0.1 # 降低隨機性，讓結果更精準
            )
            
            # 解析回傳的資料
            raw_content = response.choices[0].message.content
            result = json.loads(raw_content)
            
            return result.get("nodes", []), result.get("edges", []), None
            
        except Exception as e:
            return [], [], str(e)

    def batch_import(self, graph, nodes, edges):
        count_n = 0
        count_e = 0
        for n in nodes:
            if not graph.has_node(n["id"]):
                graph.add_node(n["id"], **n)
                count_n += 1
        for e in edges:
            if graph.has_node(e["source"]) and graph.has_node(e["target"]):
                if not graph.has_edge(e["source"], e["target"]):
                    graph.add_edge(e["source"], e["target"], label=e["label"])
                    count_e += 1
        return f"✅ Batch imported {count_n} characters and {count_e} relationships."
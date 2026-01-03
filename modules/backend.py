import networkx as nx
import json
import os
from openai import OpenAI

class GraphManager:
    def __init__(self):
        # 檢查並建立 data 資料夾
        if not os.path.exists('data'):
            os.makedirs('data')

    def get_initial_graph(self):
        """建立初始圖表 (使用有向圖 DiGraph)"""
        G = nx.DiGraph()
        # 加入預設範例資料
        G.add_node("哈利波特", title="存活下來的男孩", type="character", group=1)
        G.add_node("榮恩", title="哈利的好友", type="character", group=1)
        G.add_edge("哈利波特", "榮恩", label="摯友")
        return G

    def add_character(self, graph, name, description):
        if graph.has_node(name):
            return False, f"⚠️ 角色 '{name}' 已經存在。"
        graph.add_node(name, title=description, type="character", group=1)
        return True, f"✅ 已新增角色：{name}"

    def add_relationship(self, graph, source, target, relation):
        if graph.has_edge(source, target):
            return False, f"⚠️ 關係 '{source} -> {target}' 已經存在。"
        graph.add_edge(source, target, label=relation)
        return True, f"🔗 已連結：{source} --[{relation}]--> {target}"
    
    # --- 資料操作 (CRUD) ---
    def delete_character(self, graph, name):
        """刪除角色，同時也會移除相關連線"""
        if graph.has_node(name):
            graph.remove_node(name)
            return True, f"🗑️ 已刪除角色：{name}"
        else:
            return False, f"⚠️ 找不到角色 '{name}'。"

    def delete_relationship(self, graph, source, target):
        """刪除兩個角色之間的特定關係"""
        if graph.has_edge(source, target):
            graph.remove_edge(source, target)
            return True, f"🗑️ 已移除關係：{source} -> {target}"
        else:
            return False, f"⚠️ 找不到關係：{source} -> {target}"

    def edit_character_description(self, graph, name, new_description):
        """更新角色描述"""
        if graph.has_node(name):
            graph.nodes[name]['title'] = new_description
            return True, f"✏️ 已更新 {name} 的描述"
        else:
            return False, f"⚠️ 找不到角色 '{name}'。"
        
    def edit_relationship_label(self, graph, source, target, new_label):
        """更新關係標籤"""
        if graph.has_edge(source, target):
            graph[source][target]['label'] = new_label
            return True, f"✏️ 已更新關係：{source} --[{new_label}]--> {target}"
        else:
            return False, f"⚠️ 找不到關係：{source} -> {target}"

    # --- 檔案存取功能 ---
    def save_graph(self, graph, filename):
        try:
            filepath = f"data/{filename}.json"
            graph_data = nx.node_link_data(graph)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=4)
            return True, f"💾 專案已儲存至 {filepath}"
        except Exception as e:
            return False, f"❌ 存檔失敗：{str(e)}"

    def load_graph(self, uploaded_file):
        try:
            graph_data = json.load(uploaded_file)
            G = nx.node_link_graph(graph_data, directed=True)
            return G, f"📂 成功讀取專案：{uploaded_file.name}"
        except Exception as e:
            return None, f"❌ 讀檔失敗：{str(e)}"

    # --- AI 分析功能 ---
    def process_text_with_ai(self, text, api_key):
        """
        呼叫 LLM 進行實體關係萃取。
        支援 OpenAI 原生 API 與 Groq API。
        """
        # 檢查是否使用 Groq API (以 gsk_ 開頭)
        if api_key.startswith("gsk_"):
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            model_name = "llama-3.3-70b-versatile" 
        else:
            client = OpenAI(api_key=api_key)
            model_name = "gpt-4o"

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
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            raw_content = response.choices[0].message.content
            result = json.loads(raw_content)
            
            return result.get("nodes", []), result.get("edges", []), None
            
        except Exception as e:
            return [], [], str(e)

    def batch_import(self, graph, nodes, edges):
        """
        批次匯入資料。
        若節點不存在則新增；若關係已存在則更新標籤。
        """
        count_n = 0
        count_e = 0
        
        # 1. 匯入節點
        for n in nodes:
            node_id = n.get("id") or n.get("name")
            if node_id:
                if not graph.has_node(node_id):
                    # 僅新增不存在的角色，避免覆蓋現有描述
                    attrs = {k: v for k, v in n.items() if k not in ['id', 'name']}
                    graph.add_node(node_id, **attrs)
                    count_n += 1
                else:
                    pass
        
        # 2. 匯入關係
        for e in edges:
            source = e.get("source")
            target = e.get("target")
            label = e.get("label", "related")
            
            if source and target:
                # 若節點不存在，自動補上 (防呆)
                if not graph.has_node(source):
                    graph.add_node(source, title="Auto-generated", type="character", group=1)
                if not graph.has_node(target):
                    graph.add_node(target, title="Auto-generated", type="character", group=1)
                
                # 若關係已存在，檢查標籤是否需要更新
                if graph.has_edge(source, target):
                    if graph[source][target].get('label') != label:
                        graph[source][target]['label'] = label
                        count_e += 1
                else:
                    # 若關係不存在，直接新增
                    graph.add_edge(source, target, label=label)
                    count_e += 1
                    
        return f"✅ 已處理 {count_n} 個新角色，並更新/新增 {count_e} 條關係！"
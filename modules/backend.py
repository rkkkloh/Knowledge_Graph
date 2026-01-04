import networkx as nx
import json
import os
from openai import OpenAI

class GraphManager:
    def __init__(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # 初始化歷史紀錄堆疊
        self.history = []
        self.history_step = -1

    def _autosave(self, graph, push_history=True):
        """
        將當前圖表狀態寫入 JSON，並根據 push_history 決定是否加入歷史紀錄。
        """
        try:
            # 序列化圖表資料
            graph_data = nx.node_link_data(graph)
            
            # 寫入硬碟
            filepath = "data/autosave.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=4)
            
            # 更新歷史紀錄
            if push_history:
                # 如果目前不在最新的步驟（曾經 Undo 過），移除後續的紀錄
                if self.history_step < len(self.history) - 1:
                    self.history = self.history[:self.history_step + 1]
                
                self.history.append(graph_data)
                self.history_step += 1
                
        except Exception as e:
            print(f"Autosave failed: {e}")

    def undo(self):
        if self.history_step > 0:
            self.history_step -= 1
            data = self.history[self.history_step]
            G = nx.node_link_graph(data, directed=True)
            # 復原狀態，但不視為新操作
            self._autosave(G, push_history=False) 
            return G, f"已復原 (步驟 {self.history_step}/{len(self.history)-1})"
        return None, "已達最舊紀錄"

    def redo(self):
        if self.history_step < len(self.history) - 1:
            self.history_step += 1
            data = self.history[self.history_step]
            G = nx.node_link_graph(data, directed=True)
            self._autosave(G, push_history=False)
            return G, f"已重做 (步驟 {self.history_step}/{len(self.history)-1})"
        return None, "已是最新紀錄"

    def _load_autosave(self):
        filepath = "data/autosave.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    graph_data = json.load(f)
                G = nx.node_link_graph(graph_data, directed=True)
                
                # 若無歷史紀錄（例如剛啟動），初始化第一筆
                if not self.history:
                    self.history.append(graph_data)
                    self.history_step = 0
                return G
            except:
                return None
        return None

    def get_initial_graph(self):
        saved_graph = self._load_autosave()
        if saved_graph:
            return saved_graph
            
        G = nx.DiGraph()
        G.add_node("哈利波特", title="存活下來的男孩", type="character", group=1)
        G.add_node("榮恩", title="哈利的好友", type="character", group=1)
        G.add_edge("哈利波特", "榮恩", label="摯友")
        
        self._autosave(G, push_history=True)
        return G

    def reset_graph(self, graph):
        graph.clear()
        graph.add_node("哈利波特", title="存活下來的男孩", type="character", group=1)
        graph.add_node("榮恩", title="哈利的好友", type="character", group=1)
        graph.add_edge("哈利波特", "榮恩", label="摯友")
        
        self._autosave(graph, push_history=True)
        return True, "系統已重置為預設狀態"

    def add_character(self, graph, name, description):
        if graph.has_node(name): return False, f"角色 '{name}' 已經存在。"
        graph.add_node(name, title=description, type="character", group=1)
        self._autosave(graph, push_history=True)
        return True, f"已新增角色：{name}"

    def add_relationship(self, graph, source, target, relation):
        if graph.has_edge(source, target): return False, f"關係 '{source} -> {target}' 已經存在。"
        graph.add_edge(source, target, label=relation)
        self._autosave(graph, push_history=True)
        return True, f"已連結：{source} --[{relation}]--> {target}"
    
    def delete_character(self, graph, name):
        if graph.has_node(name):
            graph.remove_node(name)
            self._autosave(graph, push_history=True)
            return True, f"已刪除角色：{name}"
        return False, f"找不到角色 '{name}'。"

    def delete_relationship(self, graph, source, target):
        if graph.has_edge(source, target):
            graph.remove_edge(source, target)
            self._autosave(graph, push_history=True)
            return True, f"已移除關係：{source} -> {target}"
        return False, f"找不到關係：{source} -> {target}"

    def edit_character_description(self, graph, name, new_description):
        if graph.has_node(name):
            graph.nodes[name]['title'] = new_description
            self._autosave(graph, push_history=True)
            return True, f"已更新 {name} 的描述"
        return False, f"找不到角色 '{name}'。"
        
    def edit_relationship_label(self, graph, source, target, new_label):
        if graph.has_edge(source, target):
            graph[source][target]['label'] = new_label
            self._autosave(graph, push_history=True)
            return True, f"已更新關係：{source} --[{new_label}]--> {target}"
        return False, f"找不到關係：{source} -> {target}"

    def save_graph(self, graph, filename):
        try:
            filepath = f"data/{filename}.json"
            graph_data = nx.node_link_data(graph)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=4)
            return True, f"專案已儲存至 {filepath}"
        except Exception as e:
            return False, f"存檔失敗：{str(e)}"

    def load_graph(self, uploaded_file):
        try:
            graph_data = json.load(uploaded_file)
            G = nx.node_link_graph(graph_data, directed=True)
            # 讀檔視為重大變更，推入歷史
            self._autosave(G, push_history=True)
            return G, f"成功讀取專案：{uploaded_file.name}"
        except Exception as e:
            return None, f"讀檔失敗：{str(e)}"

    def process_text_with_ai(self, text, api_key):
        if api_key.startswith("gsk_"):
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            model_name = "llama-3.3-70b-versatile" 
        else:
            client = OpenAI(api_key=api_key)
            model_name = "gpt-4o"

        system_prompt = """
        你是一個知識圖譜專家。請從使用者的文本中萃取「實體(Nodes)」與「關係(Edges)」。
        請務必回傳純 JSON 格式。
        格式如下：
        {
            "nodes": [{"id": "實體名稱", "title": "描述"}],
            "edges": [{"source": "實體名稱", "target": "實體名稱", "label": "關係類型"}]
        }
        """
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
                response_format={"type": "json_object"}, temperature=0.1
            )
            raw = response.choices[0].message.content
            res = json.loads(raw)
            return res.get("nodes", []), res.get("edges", []), None
        except Exception as e:
            return [], [], str(e)

    def batch_import(self, graph, nodes, edges):
        count_n = 0
        count_e = 0
        for n in nodes:
            node_id = n.get("id") or n.get("name")
            if node_id:
                if not graph.has_node(node_id):
                    attrs = {k: v for k, v in n.items() if k not in ['id', 'name']}
                    graph.add_node(node_id, **attrs)
                    count_n += 1
        for e in edges:
            source = e.get("source")
            target = e.get("target")
            label = e.get("label", "related")
            if source and target:
                if not graph.has_node(source): graph.add_node(source, title="Auto", type="character", group=1)
                if not graph.has_node(target): graph.add_node(target, title="Auto", type="character", group=1)
                if graph.has_edge(source, target):
                    if graph[source][target].get('label') != label:
                        graph[source][target]['label'] = label; count_e += 1
                else:
                    graph.add_edge(source, target, label=label); count_e += 1
        
        self._autosave(graph, push_history=True)
        return f"已處理 {count_n} 個新實體，並更新/新增 {count_e} 條關係！"
    
    def analyze_centrality(self, graph):
        if not graph or graph.number_of_nodes() == 0: return []
        centrality = nx.degree_centrality(graph)
        return sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
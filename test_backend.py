# test_backend.py
import pytest
import networkx as nx
from modules.backend import GraphManager

# --- Fixtures ---

@pytest.fixture
def manager():
    """自動產生一個 GraphManager 實例"""
    return GraphManager()

@pytest.fixture
def empty_graph(manager):
    """自動產生一個乾淨的、空的有向圖"""
    return nx.DiGraph()

# --- 開始測試 CRUD 功能 ---

def test_add_character(manager, empty_graph):
    """測試：新增角色"""
    # 動作
    success, msg = manager.add_character(empty_graph, "Harry", "The hero")
    
    # 驗證
    assert success is True
    assert "Harry" in empty_graph.nodes
    assert empty_graph.nodes["Harry"]["title"] == "The hero"

def test_add_duplicate_character_fails(manager, empty_graph):
    """測試：重複新增應該要失敗"""
    manager.add_character(empty_graph, "Harry", "Hero")
    # 再加一次
    success, msg = manager.add_character(empty_graph, "Harry", "Duplicate")
    
    assert success is False
    assert "已經存在" in msg or "already exists" in msg

def test_add_relationship_directed(manager, empty_graph):
    """測試：有向圖關係 (A->B 不等於 B->A)"""
    manager.add_character(empty_graph, "A", "")
    manager.add_character(empty_graph, "B", "")
    
    # 新增 A -> B
    success, msg = manager.add_relationship(empty_graph, "A", "B", "Likes")
    
    assert success is True
    assert empty_graph.has_edge("A", "B")      # A 到 B 應該要有
    assert not empty_graph.has_edge("B", "A")  # B 到 A 不應該有 (因為是有向圖)

def test_delete_character(manager, empty_graph):
    """測試：刪除角色"""
    manager.add_character(empty_graph, "Voldemort", "Villain")
    
    # 執行刪除
    success, msg = manager.delete_character(empty_graph, "Voldemort")
    
    assert success is True
    assert "Voldemort" not in empty_graph.nodes

def test_delete_relationship(manager, empty_graph):
    """測試：刪除關係"""
    manager.add_character(empty_graph, "A", "")
    manager.add_character(empty_graph, "B", "")
    manager.add_relationship(empty_graph, "A", "B", "Friend")
    
    # 執行刪除
    success, msg = manager.delete_relationship(empty_graph, "A", "B")
    
    assert success is True
    assert not empty_graph.has_edge("A", "B")

def test_edit_description(manager, empty_graph):
    """測試：修改描述"""
    manager.add_character(empty_graph, "Draco", "Bad boy")
    
    # 修改
    success, msg = manager.edit_character_description(empty_graph, "Draco", "Redeemed")
    
    assert success is True
    assert empty_graph.nodes["Draco"]["title"] == "Redeemed"

def test_edit_relationship_label(manager, empty_graph):
    """測試：修改關係標籤"""
    manager.add_character(empty_graph, "A", "")
    manager.add_character(empty_graph, "B", "")
    manager.add_relationship(empty_graph, "A", "B", "Hate")
    
    # 修改
    success, msg = manager.edit_relationship_label(empty_graph, "A", "B", "Love")
    
    assert success is True
    assert empty_graph["A"]["B"]["label"] == "Love"
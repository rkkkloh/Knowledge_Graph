from streamlit.testing.v1 import AppTest
import pytest

# --- 小幫手函式：用標籤名稱來找元件 ---
def get_element_by_label(elements, label_text):
    """在元件清單中，找到 label 符合的那個元件"""
    for ele in elements:
        # 有些元件的 label 屬性可能藏在不同地方，這裡做通用處理
        if hasattr(ele, "label") and label_text in ele.label:
            return ele
    return None

# 測試 1: 檢查網頁標題與基本結構
def test_app_loads():
    at = AppTest.from_file("app.py").run()
    
    # 所以 at.title 會是空的。這裡改為檢查 markdown 元件中是否包含標題文字。
    found_title = False
    for md in at.markdown:
        if "Nexus Graph 知識圖譜編輯器" in md.value:
            found_title = True
            break
            
    assert found_title, "找不到應用程式標題"
    assert len(at.sidebar.header) > 0

# 測試 2: 測試「新增角色」功能
def test_add_character_flow():
    at = AppTest.from_file("app.py").run()
    
    # 1. 填寫角色名稱
    name_input = get_element_by_label(at.text_input, "角色名稱")
    if name_input:
        name_input.input("測試角色A").run()
    else:
        pytest.fail("找不到「角色名稱」輸入框")

    # 2. 填寫描述
    desc_input = get_element_by_label(at.text_area, "角色描述")
    if desc_input:
        desc_input.input("這是一個測試描述").run()

    # 3. 按下按鈕
    add_btn = get_element_by_label(at.button, "加入角色")
    if add_btn:
        add_btn.click().run()
    else:
        pytest.fail("找不到「加入角色」按鈕")
    
    # 4. 驗證結果
    assert not at.exception
    # 檢查 session_state 是否成功寫入
    assert "測試角色A" in at.session_state["graph"].nodes()

# 測試 3: 測試「API Key」警告機制
def test_api_key_warning():
    at = AppTest.from_file("app.py").run()
    
    # 1. 先填寫故事文本，繞過第一個警告
    text_area = get_element_by_label(at.text_area, "故事文本")
    if text_area:
        text_area.input("這是一段測試用的假故事，用來騙過第一道檢查。").run()
    else:
        pytest.fail("找不到「故事文本」輸入框")

    # 2. 找到「開始分析」按鈕並點擊
    ai_btn = get_element_by_label(at.button, "開始分析")
    
    if ai_btn:
        ai_btn.click().run()
    else:
        pytest.fail("找不到「開始分析」按鈕")
    
    # 3. 檢查是否出現錯誤警告
    # 這次因為有文字但沒有 Key，應該會出現 error (API Key 相關)
    assert len(at.error) > 0
    assert "API Key" in at.error[0].value
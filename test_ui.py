from streamlit.testing.v1 import AppTest
import pytest

def get_element_by_label(elements, label_text):
    for ele in elements:
        if hasattr(ele, "label") and label_text in ele.label:
            return ele
    return None

def test_app_loads():
    at = AppTest.from_file("app.py").run()
    found_title = False
    for md in at.markdown:
        if "Nexus Graph 知識圖譜編輯器" in md.value:
            found_title = True
            break
    assert found_title, "找不到應用程式標題"
    assert len(at.sidebar.header) > 0, "找不到側邊欄"

def test_add_character_flow():
    at = AppTest.from_file("app.py").run()
    
    name_input = get_element_by_label(at.text_input, "角色名稱")
    if name_input:
        name_input.input("測試角色A").run()
    else:
        pytest.fail("找不到「角色名稱」輸入框")

    desc_input = get_element_by_label(at.text_area, "角色描述")
    if desc_input:
        desc_input.input("這是一個測試描述").run()

    add_btn = get_element_by_label(at.button, "加入角色")
    if add_btn:
        add_btn.click().run()
    else:
        pytest.fail("找不到「加入角色」按鈕")
    
    assert not at.exception
    assert "測試角色A" in at.session_state["graph"].nodes()

def test_api_key_warning():
    at = AppTest.from_file("app.py").run()
    
    text_area = get_element_by_label(at.text_area, "故事文本")
    if text_area:
        text_area.input("這是一段測試用的假故事。").run()
    else:
        pytest.fail("找不到「故事文本」輸入框")

    ai_btn = get_element_by_label(at.button, "開始分析")
    if ai_btn:
        ai_btn.click().run()
    else:
        pytest.fail("找不到「開始分析」按鈕")
    
    has_error = False
    for err in at.error:
        if "API Key" in err.value:
            has_error = True
            break
            
    assert has_error, "沒有跳出 API Key 錯誤警告"
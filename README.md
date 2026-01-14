# Nexus Graph | 互動式故事知識圖譜建構工具

**Nexus Graph** 是一個結合 **AI 智慧萃取** 與 **手動編輯** 的工具，透過圖形介面，可以輕鬆建構、視覺化並分析複雜的角色關係網絡。

## ✨ Features

- **💻 AI 智慧分析**：整合 OpenAI / Groq API，貼上故事文本即可自動萃取角色與關係。
- **🕸️ 互動式視覺化**：使用物理引擎 (Physics-based) 繪製網絡圖，支援縮放、拖曳與動態調整。
- **➡️ 有向圖支援 (Directed Graph)**：精準表達單向與雙向關係，並具備箭頭視覺引導。
- **🛠️ 完整的 CRUD 編輯**：支援新增、修改、刪除角色與關係，並具備防止重複的防呆機制。
- **💾 專案管理**：支援匯出/匯入 JSON 格式，方便儲存與分享知識圖譜。
- **🏆 關鍵角色分析**：自動計算並顯示圖譜中最重要的角色 Top 5。
- **🧪 自動化測試**：內建單元測試，確保後端邏輯的穩定性。

---

## 📂 Architecture

本專案採用 **模組化 (Modular)** 設計，將介面、邏輯與視覺化分離，提升維護性：

### 1. `app.py` (Frontend Entry)

- **角色**：程式入口與排版中心。
- **功能**：負責 Streamlit 的頁面佈局、側邊欄控制、Tabs 分頁切換，以及接收使用者輸入。

### 2. `modules/backend. py` (Core Logic)

- **角色**：應用程式的大腦。
- **功能**：
  - 封裝 `GraphManager` 類別。
  - 處理 NetworkX 圖形演算法 (CRUD)。
  - 串接 OpenAI / Groq API 進行文本分析。
  - 負責 JSON 檔案的存取與讀寫。
  - 實作 Undo/Redo 機制與中心性分析。

### 3. `modules/ui.py` (UI Components)

- **角色**：使用者介面元件。
- **功能**：
  - 渲染側邊欄控制台（API 設定、專案管理、檢視設定）。
  - 渲染主要功能分頁（新增、連結、AI、管理）。
  - 整合鍵盤快捷鍵監聽。

### 4. `modules/visualization.py` (Visualization Engine)

- **角色**：視覺化渲染引擎。
- **功能**：
  - 負責將 NetworkX 轉換為 PyVis 互動圖表。
  - **JavaScript 注入**：處理進階功能（如：記憶節點位置、鏡頭縮放狀態、雙擊置中）。

### 5. `assets/style.css` (Styling)

- **角色**：全域樣式表。
- **功能**：
  - 統一深色主題配色（#131314 背景、#1E1F20 側邊欄）。
  - 自定義按鈕、輸入框、Tab 標籤等元件樣式。
  - 優化捲軸、Spinner、Alert 等細節。

### 6. `test_backend.py` & `test_ui.py` (Unit Tests)

- **功能**：針對後端邏輯與前端互動進行自動化測試，確保新增、刪除、編輯等功能運作正常。

---

## 🚀 Quick Start

### 1. 環境準備

確保您的電腦已安裝 Python 3.8 或以上版本。

```bash
# 1. Clone 專案
git clone https://github.com/david911226/Knowledge_Graph.git
cd Knowledge_Graph

# 2. 建立並啟動虛擬環境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. 安裝依賴套件

包含 Streamlit, NetworkX, PyVis, OpenAI 以及測試用的 Pytest。

```bash
pip install -r requirements.txt
```

### 3. 設定 API Key（可選）

若要使用 AI 智慧分析功能，請準備以下其中一種 API Key：

- **Groq API**（免費）：前往 [Groq Console](https://console.groq.com/keys) 註冊並產生
- **OpenAI API**：前往 [OpenAI Platform](https://platform.openai.com/api-keys) 取得

啟動程式後，在側邊欄的「API 設定」區塊輸入即可。

### 4. 啟動程式

```bash
streamlit run app.py
```

程式會自動在瀏覽器開啟 `http://localhost:8501`

---

## 🧪 Testing & Validation

本專案包含完整的單元測試，用於驗證後端邏輯與前端互動的正確性。

### 1. 執行測試

請在終端機（確保已進入 `venv`）執行以下指令：

```bash
# 執行所有測試
python -m pytest

# 執行測試並產生 HTML 報告
python -m pytest --html=report.html
```

### 2. 查看測試結果

- **終端機回饋**：若看到綠色的 `PASSED`，代表功能正常。
- **網頁報告**：執行後會產生 `report.html` 檔案。
  - **Mac**:  在終端機輸入 `open report.html` 即可開啟。
  - **Windows**: 在檔案總管雙擊該檔案，或輸入 `start report.html`。
  - 這份報告詳細列出了每個測試案例（新增、刪除、防呆機制）的執行結果。

---

## 📖 操作指南

### 1. 手動建立角色與關係

- 切換至「👤 新增」分頁，輸入角色名稱與描述。
- 切換至「🔗 連結」分頁，選擇來源與目標角色，並定義關係類型。

### 2. AI 智慧分析

- 在側邊欄輸入 API Key。
- 切換至「💻 AI」分頁，貼上故事文本。
- 點擊「開始分析」，AI 會自動萃取角色與關係。
- 審核結果後，點擊「✅ 確認匯入」即可加入圖譜。

### 3. 視覺化互動

- **拖曳**節點可調整位置（系統會自動記憶）。
- **滑鼠滾輪**縮放視圖。
- **雙擊空白處**重置視角。

### 4. 編輯與管理

- 切換至「⚙️ 管理」分頁，可以：
  - 刪除角色或關係
  - 修改角色描述或關係標籤

### 5. 專案管理

- **儲存**：在側邊欄「💾 專案管理」輸入檔名，點擊「Save」。
- **載入**：上傳先前儲存的 JSON 檔案，點擊「Load Project」。

### 6. 其他功能

- **Undo/Redo**：使用側邊欄按鈕或鍵盤快捷鍵 `Ctrl+Z` / `Ctrl+Shift+Z`。
- **搜尋聚焦**：在「👀 檢視設定」選擇角色，圖譜會自動聚焦該節點。
- **Reset**：清空整個圖譜，重新開始。
- **關鍵角色 Top 5**：查看圖譜中連接數最多的角色排名。

---

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Web Framework**: Streamlit
- **Graph Engine**: NetworkX (DiGraph)
- **Visualization**:  PyVis (with JavaScript injection)
- **AI Model**: OpenAI GPT-4o / GPT-3.5-turbo, Groq Llama
- **Styling**: Custom CSS
- **Testing**: Pytest

---

## 📂 Project Structure

```
Knowledge_Graph/
├── app.py                    # 主程式入口
├── modules/
│   ├── backend.py            # 後端邏輯與圖形管理
│   ├── ui.py                 # UI 元件渲染
│   └── visualization.py      # 圖形視覺化引擎
├── assets/
│   └── style.css             # 全域樣式表
├── pages/
│   └── test_page.py          # 測試執行器頁面
├── test_backend.py           # 後端單元測試
├── test_ui.py                # UI 單元測試
├── requirements. txt          # 依賴套件清單
└── README.md                 # 專案說明文件
```

---

## 📝 Team

- **Backend & Logic**: 羅睿康
- **Frontend & UI**: 陳冠謙

---

## 🙏 Acknowledgements

感謝以下開源專案：

- [Streamlit](https://streamlit.io/) - 快速建構互動式 Web 應用
- [NetworkX](https://networkx.org/) - 強大的圖形演算法庫
- [PyVis](https://pyvis.readthedocs.io/) - 互動式網絡視覺化
- [OpenAI](https://openai.com/) / [Groq](https://groq.com/) - AI 文本分析引擎

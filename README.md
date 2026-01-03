# Nexus Graph | 互動式故事知識圖譜建構工具

**Nexus Graph** 是一個結合 **AI 智慧萃取** 與 **手動編輯** 的強大工具，專為創作者、研究人員與讀者設計。透過直觀的圖形介面，您可以輕鬆建構、視覺化並管理複雜的角色關係網絡。

## ✨ Features (功能特色)

- **🤖 AI 智慧分析**：整合 OpenAI GPT 模型，貼上故事文本即可自動萃取角色與關係。
- **🕸️ 互動式視覺化**：使用物理引擎 (Physics-based) 繪製網絡圖，支援縮放、拖曳與動態調整。
- **➡️ 有向圖支援 (Directed Graph)**：精準表達單向 (師徒) 與雙向 (朋友) 關係，並具備箭頭視覺引導。
- **🛠️ 完整的 CRUD 編輯**：支援新增、修改、刪除角色與關係，並具備防止重複的防呆機制。
- **🧪 自動化測試**：內建單元測試，確保後端邏輯的穩定性。

---

## 📂 Architecture (專案架構)

本專案採用 **模組化 (Modular)** 設計，將介面、邏輯與視覺化分離，提升維護性：

### 1. `app.py` (Frontend Entry)

- **角色**：程式入口與排版中心。
- **功能**：負責 Streamlit 的頁面佈局、側邊欄控制、Tabs 分頁切換，以及接收使用者輸入。

### 2. `modules/backend.py` (Core Logic)

- **角色**：應用程式的大腦。
- **功能**：
- 封裝 `GraphManager` 類別。
- 處理 NetworkX 圖形演算法 (CRUD)。
- 串接 OpenAI API 進行文本分析。
- 負責 JSON 檔案的存取與讀寫。

### 3. `modules/visualization.py` (Visualization Engine)

- **角色**：視覺化渲染引擎。
- **功能**：
- 負責將 NetworkX 轉換為 PyVis 互動圖表。
- **JavaScript 注入**：處理進階功能（如：記憶節點位置、鏡頭縮放狀態、雙擊置中）。

### 4. `test_backend.py` (Unit Tests)

- **功能**：針對後端邏輯進行自動化測試，確保新增、刪除、編輯等功能運作正常。

---

## 🚀 Quick Start (快速開始)

### 1. 環境準備

確保您的電腦已安裝 Python 3.8 或以上版本。

```bash
# 1. Clone 專案
git clone https://github.com/your-username/Knowledge_Graph.git
cd Knowledge_Graph

# 2. 建立並啟動虛擬環境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

```

### 2. 安裝依賴套件

包含 Streamlit, NetworkX, OpenAI 以及測試用的 Pytest。

```bash
pip install -r requirements.txt
pip install pytest pytest-html  # 若 requirements 未包含測試套件，請手動安裝

```

### 3. 啟動程式

```bash
streamlit run app.py

```

---

## 🧪 Testing & Validation (測試與驗證)

本專案包含完整的單元測試，用於驗證後端邏輯的正確性。

### 1. 執行測試

請在終端機（確保已進入 `venv`）執行以下指令：

```bash
# 執行測試並產生 HTML 報告
python -m pytest --html=report.html

```

### 2. 查看測試結果

- **終端機回饋**：若看到綠色的 `PASSED`，代表功能正常。
- **網頁報告**：執行後會產生 `report.html` 檔案。
- **Mac**: 在終端機輸入 `open report.html` 即可開啟。
- **Windows**: 在檔案總管雙擊該檔案，或輸入 `start report.html`。
- 這份報告詳細列出了每個測試案例（新增、刪除、防呆機制）的執行結果。

---

## 📖 操作指南

1. **手動編輯**：使用「新增/連結」分頁建立基礎資料。
2. **AI 分析**：切換至「AI 智慧萃取」，貼上小說文本，讓 AI 自動生成。
3. **視覺化互動**：

- **拖曳**節點可固定位置（系統會自動記憶）。
- **雙擊**空白處可重置視角。

4. **專案管理**：支援將目前的進度存檔 (`Save`) 或讀取舊檔 (`Load`)。

---

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Web Framework**: Streamlit
- **Graph Engine**: NetworkX (DiGraph)
- **Visualization**: PyVis (JavaScript injected)
- **AI Model**: OpenAI GPT-4o / GPT-3.5-turbo
- **Testing**: Pytest

---

## 📝 Team

- **Backend & Logic**: 陳冠謙
- **Frontend & UI**: 羅睿康

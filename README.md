# Nexus Graph | 互動式故事知識圖譜建構工具

**Nexus Graph** 是一個結合 **AI 智慧萃取** 與 **手動編輯** 的強大工具，專為創作者、研究人員與讀者設計。透過直觀的圖形介面，您可以輕鬆建構、視覺化並管理複雜的角色關係網絡。

## ✨ Features

- **🤖 AI 智慧分析**：整合 OpenAI GPT 模型，貼上故事文本即可自動萃取角色與關係。
- **🕸️ 互動式視覺化**：使用物理引擎 (Physics-based) 繪製網絡圖，支援縮放、拖曳與動態調整。
- **➡️ 有向圖支援 (Directed Graph)**：精準表達單向 (師徒) 與雙向 (朋友) 關係，並具備箭頭視覺引導。
- **🛠️ 完整的編輯功能**：
- **CRUD 管理**：支援新增、修改、刪除角色與關係。
- **屬性設定**：可自訂角色描述與關係類型。

- **💾 專案持久化**：支援 JSON 格式的存檔與讀檔，隨時保存您的創作進度。

---

## 📂 Architecture

本專案採用 **模組化 (Modular)** 設計，確保程式碼的擴充性與維護性：

### 1. `app.py` (Frontend)

- **角色**：應用程式的入口與外觀。
- **技術**：Streamlit, PyVis。
- **功能**：負責繪製側邊欄、分頁 (Tabs)、表單輸入，以及將圖譜渲染為 HTML 互動圖表。

### 2. `modules/backend.py` (Backend)

- **角色**：應用程式的大腦。
- **技術**：NetworkX (DiGraph), OpenAI API。
- **功能**：
- `GraphManager` 類別封裝了所有邏輯。
- 處理圖形演算法、檢查重複、增刪改查 (CRUD)。
- 負責與 OpenAI API 溝通進行文本分析。
- 處理 JSON 檔案的序列化與反序列化。

### 3. `data/`

- 用來存放使用者儲存的專案檔案 (`.json`)。

---

## 🚀 Quick Start

### 1. 環境準備

確保您的電腦已安裝 Python 3.8 或以上版本。

```bash
# 1. Clone 專案 (若已下載可跳過)
git clone https://github.com/your-username/Knowledge_Graph.git
cd Knowledge_Graph

# 2. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

```

### 2. 安裝依賴套件

我們已將所有必要的套件列於清單中。

```bash
pip install -r requirements.txt

```

### 3. 設定 OpenAI API Key (選用)

若要使用 AI 自動分析功能，您需要一組 OpenAI API Key。

- 啟動程式後，可在左側側邊欄輸入 Key。

### 4. 啟動程式

請使用 Streamlit 指令啟動主程式：

```bash
streamlit run app.py

```

---

## 📖 操作指南

1. **新增資料**：使用左側的「新增角色」或「建立關係」分頁手動輸入。
2. **AI 分析**：切換至「AI 智慧萃取」分頁，貼上小說文本，讓 AI 自動生成圖譜。
3. **編輯/刪除**：在側邊欄的專案控制區，可選擇既有角色進行修改或刪除。
4. **存取進度**：輸入專案名稱並點擊 Save，檔案將儲存於 `data/` 資料夾中。

---

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Web Framework**: Streamlit
- **Graph Engine**: NetworkX (DiGraph)
- **Visualization**: PyVis (JavaScript based)
- **AI Model**: OpenAI GPT-4o / GPT-3.5-turbo

---

## 📝 Team

- **Backend & Logic**: 陳冠謙
- **Frontend & UI**: 羅睿康

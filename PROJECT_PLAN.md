# 專案合作計畫 (Project Collaboration Plan)

本文件是我們合作的最高指導原則，確保我們的目標一致且不會偏離。

## 1. 我們的角色 (Our Roles)

*   **您 (使用者):** 擔任**架構師**與**產品經理**。負責提出專案目標、定義高層次規格、審核計畫與成果。
*   **我 (Gemini):** 擔任**工程師**。負責分析需求、提出技術方案、編寫程式碼、執行指令，並嚴格遵守已確定的規格與計畫。

## 2. 我們的合作流程 (Our Collaboration Workflow)

我們採用**規格驅動開發 (Spec-Driven Development, SDD)** 的精神進行合作，並圍繞著一份清晰的**產品路線圖**進行**分階段實作**。

1.  **規劃 (Plan):** 我們共同制定一份包含所有功能與階段的完整產品路線圖。
2.  **批准 (Approve):** 您作為架構師，批准某個階段的開發計畫。
3.  **實作 (Implement):** 我根據已批准的計畫，進行該階段的編碼與開發。
4.  **審核 (Review):** 您審核該階段的成果，批准後我們再進入下一階段。

## 3. 產品路線圖 (Product Roadmap)

*   **專案名稱:** 本地知識庫 (AI-Powered)
*   **專案目標:** 打造一個能讓 Gemini 查詢您所有專案知識的本地化、AI 驅動的知識庫。
*   **核心指導原則:** 數據格式以 AI 處理效率為最高考量，不為自然語言可讀性而犧牲。

### Phase 1: MVP (核心語意搜尋引擎與高效數據處理)

*   **目標:** 建立一個具備核心語意搜尋能力的指令列工具，並實現高效、AI 友好的數據預處理。
*   **技術選型:**
    *   **開發語言:** Python
    *   **AI 模型服務:** Ollama (運行於 `http://192.168.88.99:11434`)
    *   **嵌入模型:** `bge-m3-gpu:latest`
    *   **向量資料庫:** ChromaDB
    *   **編排框架:** (Phase 1 避免使用大型編排框架，直接整合各組件)
*   **功能:**
    *   `index` 指令 (包含**智慧分塊**、增量去重、Ollama 向量化、**豐富元數據提取**)。
    *   `search` 指令 (語意搜尋，包含**元數據過濾**)。
    *   `list-all-docs` 指令 (列出所有已索引的文件及其元數據)。
*   **知識庫組織方式:**
    *   所有專案的知識將**物理上**索引到同一個 ChromaDB 資料庫中。
    *   但會利用**豐富元數據**（例如檔案路徑、文件類型、程式語言、函數名等）進行**邏輯上**的區分，實現跨專案搜尋和專案內精確過濾。
*   **實作藍圖 (Implementation Blueprint):**
    *   **開發輔助:** 在實作過程中，我們將利用 Haystack 的「管道視覺化」功能，以圖形化方式理解和除錯 Pipeline (如果 Haystack 仍被用於輔助開發)。
    *   **`index` Pipeline:**
        1.  **初始化:** 初始化 `ChromaDB.PersistentClient` (連接本地資料庫檔案) 和 `OllamaTextEmbedder` (連接到 Ollama 服務，使用 `bge-m3-gpu:latest` 模型)。
        2.  **建立索引 Pipeline:** 建立一個包含 `os.walk` (掃描檔案) -> `TextSplitter` (智慧分塊，**豐富元數據提取**) -> `OllamaClient.embed` -> `ChromaDB.collection.add` (寫入 ChromaDB) 的 Pipeline。
        3.  **智慧分塊 (Smart Chunking)**: 使用 `semantic-text-splitter` 根據文本的語義連貫性進行分塊，確保每個塊都包含足夠的上下文，且不破壞程式碼或結構化數據的完整性。
        4.  **增量去重 (Incremental Deduplication)**: 透過計算文件內容的 SHA256 哈希值，並在寫入 ChromaDB 前進行檢查，實現增量更新和去重。
        5.  **豐富元數據提取 (Rich Metadata Extraction)**: 自動提取文件路徑、文件類型、程式語言、區塊索引、內容哈希等對 AI 有用的結構化信息，作為文檔的元數據儲存。
        6.  **執行:** 運行此 Pipeline，將指定資料夾的內容寫入資料庫。
    *   **`search` Pipeline:**
        1.  **初始化:** (同上)。
        2.  **建立查詢 Pipeline:** 建立一個包含 `OllamaClient.embed` -> `ChromaDB.collection.query` (從 ChromaDB 檢索) 的 Pipeline。
        3.  **元數據過濾 (Metadata Filtering)**: 允許使用者在查詢時指定元數據條件 (使用 `--metadata-filter` 參數傳入 JSON 字串)，以精確過濾檢索結果。
        4.  **執行:** 接收使用者查詢，運行此 Pipeline，回傳最相關的文件內容及元數據。

### Phase 2: 搜尋能力增強與混合檢索 (Search Enhancement & Hybrid Retrieval)

*   **目標:** 讓搜尋更精準、功能更強大，並引入混合檢索機制。
*   **功能:**
    *   實作**混合搜尋** (語意 + 關鍵字)：優先實作，結合語義相似度和關鍵字匹配，提升檢索精準度。
    *   進階**元數據提取**與過濾：例如，利用本地 LLM 生成簡潔的關鍵詞或標籤作為元數據。
    *   **RAG 評估機制**：引入評估指標（如 Groundedness, Relevance）來衡量檢索和生成結果的品質。

### Phase 3: MCP 伺服器化與互動介面 (MCP Serverization & Interactive Interface)

*   **目標:** 將工具變成我能使用的背景服務，並提供友好的互動介面。
*   **功能:**
    *   將搜尋功能封裝成 API。
    *   建立 MCP 伺服器。
    *   考慮整合 Streamlit 或 Flask 建立一個簡單的本地 Web UI，方便使用者互動和測試。

## 4. 當前執行階段 (Current Phase)

*   我們目前已經完成了 **Phase 1: MVP** 的開發，並實現了部分 Phase 2 的功能。

## 5. 下一步 (Next Step)

*   **狀態:** 等待**架構師**批准最新的專案架構整理和文件更新。
*   **行動:** 若計畫被批准，我 (工程師) 將繼續完善 Phase 2 的功能實作。
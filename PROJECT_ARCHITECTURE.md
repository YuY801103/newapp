# 專案架構文件 (最新版本)

## 專案概述

本專案是一個本地化的AI驅動知識庫系統，旨在讓大型語言模型(Gemini)能夠查詢和理解用戶的所有專案知識。系統通過預處理、索引和搜尋三個主要階段來實現這一目標。

## 核心組件

### 1. 資料預處理模組

#### `flexible_preprocessing.py`
- 通用預處理模組，自動提取實體和生成元數據
- 功能包括：
  - 通用實體識別（硬體型號、技術術語等）
  - 內容類型分類（推薦、警告、技術內容等）
  - 關鍵詞提取
  - 文本結構分析

#### `improved_deduplication.py`
- 改進的重複檢測和處理模組
- 防止相同內容被多次索引
- 提高存儲效率和搜尋準確性

### 2. 知識庫索引模組

#### `optimized_indexing.py`
- 優化的索引腳本，整合預處理功能和重複處理
- 功能包括：
  - 智慧分塊（根據語義連貫性進行分塊）
  - 增量去重（通過SHA256雜湊值檢查）
  - 豐富元數據提取
  - Ollama向量化處理
  - ChromaDB存儲

### 3. 搜尋引擎模組

#### `universal_hybrid_search.py`
- 通用混合搜尋模組，結合語意和關鍵詞搜尋
- 功能包括：
  - 語意搜尋（使用bge-m3-gpu模型）
  - 關鍵詞搜尋
  - 元數據過濾
  - 結果加權和排序

#### `optimized_search.py`
- 優化的搜尋腳本，提供豐富的搜尋選項
- 支援互動式搜尋模式

### 4. 命令行介面

#### `main.py`
- 主要的命令行介面
- 提供index、search、list-all-docs指令
- 實現基本的知識庫操作功能

#### `preprocess_cli.py`
- 預處理命令行工具
- 提供預處理、搜尋、顯示元數據等功能

## 資料流

1. **預處理階段**：
   - 使用`flexible_preprocessing.py`對文件進行分析
   - 提取實體、分類內容、生成關鍵詞
   - 生成結構化元數據

2. **索引階段**：
   - 使用`optimized_indexing.py`處理文件
   - 智慧分塊確保語義完整性
   - 重複檢測避免冗餘索引
   - 使用Ollama生成向量嵌入
   - 存儲到ChromaDB向量資料庫

3. **搜尋階段**：
   - 使用`universal_hybrid_search.py`進行混合搜尋
   - 結合語意相似度和關鍵詞匹配
   - 根據元數據過濾結果
   - 提供加權排序的搜尋結果

## 技術棧

- **開發語言**：Python
- **AI模型服務**：Ollama (運行於 `http://192.168.88.99:11434`)
- **嵌入模型**：`bge-m3-gpu:latest`
- **向量資料庫**：ChromaDB
- **文本處理**：semantic-text-splitter
- **命令行介面**：Typer

## 資料存儲

- **向量資料庫**：`./chroma_db`目錄
- **索引追蹤**：`indexed_hashes.txt`文件記錄已索引內容的雜湊值
- **元數據緩存**：`preprocessed_metadata.json`文件存儲預處理結果

## 使用方法

### 索引內容
```bash
python optimized_indexing.py index /path/to/content
```

### 搜尋內容
```bash
python optimized_search.py search "查詢內容"
```

### 互動式搜尋
```bash
python optimized_search.py interactive-search
```

### 預處理操作
```bash
# 預處理指定目錄的內容
python preprocess_cli.py preprocess /path/to/content

# 搜尋內容
python preprocess_cli.py search "IMU 推薦"

# 顯示特定文件的元數據
python preprocess_cli.py show-metadata /path/to/file.md
```
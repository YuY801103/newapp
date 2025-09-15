#!/usr/bin/env python3
"""
通用的預處理腳本，適用於多專案知識庫
"""

import re
import json
from typing import List, Dict, Any

class FlexiblePreprocessor:
    """通用的預處理器"""
    
    def __init__(self):
        # 通用的實體類型模式
        self.entity_patterns = {
            "hardware_models": [
                r'[A-Z0-9]+-[A-Z0-9]+',  # 通用硬體型號模式 (如 MPU-9250, ICM-20948)
                r'[A-Z0-9]+[A-Z0-9\-]*[0-9]+[A-Z0-9]*'  # 更廣泛的型號模式
            ],
            "recommendations": [
                r'推薦', r'建議', r'recommend', r'suggested', r'優先',
                r'preferred', r'best', r'optimal'
            ],
            "warnings": [
                r'注意', r'警告', r'warning', r'caution', r'小心',
                r'not recommended', r'避免', r'do not'
            ],
            "technical_terms": [
                r'IMU', r'陀螺儀', r'加速度計', r'磁力計', r'sensor',
                r'accelerometer', r'gyroscope', r'magnetometer'
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        從文本中提取各種實體
        """
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            found_entities = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                found_entities.extend(matches)
            
            # 去重並過濾空字符串
            entities[entity_type] = list(set(filter(None, found_entities)))
        
        return entities
    
    def classify_content(self, text: str) -> str:
        """
        根據內容特徵進行分類
        """
        # 計算各類關鍵詞的出現次數
        recommendation_score = sum(1 for keyword in self.entity_patterns["recommendations"] 
                                 if re.search(keyword, text, re.IGNORECASE))
        warning_score = sum(1 for keyword in self.entity_patterns["warnings"] 
                          if re.search(keyword, text, re.IGNORECASE))
        technical_score = sum(1 for keyword in self.entity_patterns["technical_terms"] 
                            if re.search(keyword, text, re.IGNORECASE))
        
        # 根據分數決定內容類型
        if recommendation_score > 0 and recommendation_score >= max(warning_score, technical_score):
            return "推薦/建議"
        elif warning_score > 0 and warning_score >= max(recommendation_score, technical_score):
            return "警告/注意事項"
        elif technical_score > 0 and technical_score >= max(recommendation_score, warning_score):
            return "技術內容"
        else:
            return "一般內容"
    
    def generate_keywords(self, text: str, extracted_entities: Dict[str, List[str]]) -> List[str]:
        """
        生成通用關鍵詞
        """
        keywords = []
        
        # 添加提取的實體作為關鍵詞
        for entity_list in extracted_entities.values():
            keywords.extend(entity_list)
        
        # 添加技術術語
        for term in self.entity_patterns["technical_terms"]:
            if re.search(term, text, re.IGNORECASE):
                keywords.append(term)
        
        # 去重並返回
        return list(set(keywords))
    
    def preprocess_chunk(self, chunk_content: str, chunk_metadata: dict) -> dict:
        """
        預處理單個文本分塊
        """
        # 提取實體
        entities = self.extract_entities(chunk_content)
        
        # 內容分類
        content_type = self.classify_content(chunk_content)
        
        # 生成關鍵詞
        keywords = self.generate_keywords(chunk_content, entities)
        
        # 創建增強的元數據
        enhanced_metadata = {
            "original_metadata": str(chunk_metadata),  # 轉換為字符串
            "extracted_entities": str(entities),  # 轉換為字符串以避免嵌套字典問題
            "content_type": content_type,
            "keywords": ", ".join(keywords),  # 轉換為字符串
            "content_length": len(chunk_content)
        }
        
        return enhanced_metadata

def test_flexible_preprocessing():
    """
    測試通用預處理功能
    """
    print("測試通用預處理功能")
    print("=" * 30)
    
    # 創建預處理器
    preprocessor = FlexiblePreprocessor()
    
    # 測試文本
    test_text = """
    IMU (and barometer²) board|GY‑91, MPU-9265 (or other MPU‑9250/MPU‑6500 board)
    ICM20948V2 (ICM‑20948)³
    GY-521 (MPU-6050)³⁻¹|<img src="docs/img/gy-91.jpg" width=90 align=center>
    
    這是一個推薦的IMU選擇。GY-91整合了MPU-9250和氣壓計。
    注意：MPU-6050僅支持I²C接口（不推薦）。
    """
    
    # 創建測試元數據
    test_metadata = {
        "file_name": "test.md",
        "file_path": "./test/test.md",
        "chunk_index": 0,
        "language": "Markdown"
    }
    
    # 預處理
    enhanced_metadata = preprocessor.preprocess_chunk(test_text, test_metadata)
    
    print("增強的元數據:")
    print(json.dumps(enhanced_metadata, ensure_ascii=False, indent=2))
    
    return enhanced_metadata

if __name__ == "__main__":
    test_flexible_preprocessing()
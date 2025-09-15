#!/usr/bin/env python3
"""
改進的重複檢測和處理模組
"""

import chromadb
import hashlib
from typing import List, Dict, Any, Optional

class ImprovedDeduplication:
    """改進的重複檢測和處理類"""
    
    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="knowledge_base")
    
    def calculate_content_hash(self, content: str) -> str:
        """
        計算內容的 SHA256 雜湊值
        
        Args:
            content: 要計算雜湊的內容
            
        Returns:
            內容的 SHA256 雜湊值
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def check_duplicate_by_hash(self, content_hash: str) -> bool:
        """
        根據內容雜湊檢查是否已存在
        
        Args:
            content_hash: 內容的 SHA256 雜湊值
            
        Returns:
            如果已存在則返回 True，否則返回 False
        """
        try:
            # 使用 where 子句查詢具有相同 content_hash 的文檔
            results = self.collection.get(
                where={"content_hash": content_hash},
                include=['metadatas']
            )
            return len(results['ids']) > 0
        except Exception as e:
            print(f"檢查重複時出錯: {e}")
            return False
    
    def check_duplicate_by_content(self, content: str) -> bool:
        """
        根據內容檢查是否已存在
        
        Args:
            content: 要檢查的內容
            
        Returns:
            如果已存在則返回 True，否則返回 False
        """
        content_hash = self.calculate_content_hash(content)
        return self.check_duplicate_by_hash(content_hash)
    
    def add_document_with_deduplication(self, 
                                      content: str, 
                                      metadata: Dict[str, Any], 
                                      doc_id: str) -> bool:
        """
        添加文檔並進行重複檢測
        
        Args:
            content: 文檔內容
            metadata: 文檔元數據
            doc_id: 文檔 ID
            
        Returns:
            如果成功添加則返回 True，如果已存在則返回 False
        """
        # 計算內容雜湊
        content_hash = self.calculate_content_hash(content)
        
        # 檢查是否已存在
        if self.check_duplicate_by_hash(content_hash):
            print(f"文檔已存在 (內容雜湊: {content_hash})")
            return False
        
        # 添加新的元數據字段
        metadata["content_hash"] = content_hash
        
        try:
            # 添加到集合
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            print(f"文檔已添加 (ID: {doc_id})")
            return True
        except Exception as e:
            print(f"添加文檔時出錯: {e}")
            return False
    
    def get_document_count(self) -> int:
        """
        獲取文檔總數
        
        Returns:
            文檔總數
        """
        try:
            results = self.collection.get(include=[])
            return len(results['ids'])
        except Exception as e:
            print(f"獲取文檔數量時出錯: {e}")
            return 0

def test_deduplication():
    """
    測試重複檢測功能
    """
    print("測試改進的重複檢測功能")
    print("=" * 30)
    
    # 創建重複檢測實例
    dedup = ImprovedDeduplication()
    
    # 清理測試集合
    try:
        dedup.client.delete_collection(name="test_collection")
    except:
        pass
    
    # 創建測試集合
    test_collection = dedup.client.get_or_create_collection(name="test_collection")
    
    # 測試內容
    test_content = "這是一個測試文檔內容，用於測試重複檢測功能。"
    test_metadata = {
        "source": "test",
        "type": "test_document"
    }
    
    # 第一次添加
    print("第一次添加文檔...")
    try:
        # 計算內容雜湊
        content_hash = hashlib.sha256(test_content.encode('utf-8')).hexdigest()
        test_metadata_with_hash = test_metadata.copy()
        test_metadata_with_hash["content_hash"] = content_hash
        
        test_collection.add(
            documents=[test_content],
            metadatas=[test_metadata_with_hash],
            ids=["test_doc_1"]
        )
        print("第一次添加成功")
    except Exception as e:
        print(f"第一次添加失敗: {e}")
    
    # 第二次添加相同內容但使用我們的重複檢測
    print("第二次添加相同內容...")
    try:
        # 使用我們的重複檢測功能
        dedup_test_collection = dedup.client.get_or_create_collection(name="test_collection")
        dedup_instance = ImprovedDeduplication()
        dedup_instance.collection = dedup_test_collection
        
        result = dedup_instance.add_document_with_deduplication(
            test_content,
            test_metadata.copy(),
            "test_doc_2"
        )
        
        if result:
            print("第二次添加成功 (相同內容但不同 ID)")
        else:
            print("第二次添加失敗 (檢測到重複內容)")
    except Exception as e:
        print(f"第二次添加失敗: {e}")
    
    # 檢查集合中的文檔數量
    results = test_collection.get(include=['documents', 'metadatas'])
    print(f"集合中總共有 {len(results['ids'])} 個文檔")
    
    # 清理測試集合
    try:
        dedup.client.delete_collection(name="test_collection")
    except:
        pass

if __name__ == "__main__":
    test_deduplication()
#!/usr/bin/env python3
"""
測試改進的重複處理功能
"""

import typer
from optimized_indexing import OptimizedIndexer
from improved_deduplication import ImprovedDeduplication
import chromadb
import os

app = typer.Typer()

@app.command()
def test_deduplication():
    """測試重複處理功能"""
    typer.echo("測試改進的重複處理功能")
    
    # 創建測試數據
    test_content = "這是一個測試文檔內容，用於測試重複處理功能。"
    
    # 創建重複檢測實例
    dedup = ImprovedDeduplication()
    
    # 測試重複檢測
    is_duplicate = dedup.check_duplicate_by_content(test_content)
    typer.echo(f"內容重複檢查結果: {is_duplicate}")
    
    # 清理測試集合
    try:
        dedup.client.delete_collection(name="test_collection")
    except:
        pass
    
    # 創建測試集合
    test_collection = dedup.client.get_or_create_collection(name="test_collection")
    
    # 測試添加文檔
    test_metadata = {
        "source": "test",
        "type": "test_document"
    }
    
    # 第一次添加
    result1 = dedup.add_document_with_deduplication(
        test_content,
        test_metadata.copy(),
        "test_doc_1"
    )
    typer.echo(f"第一次添加結果: {result1}")
    
    # 第二次添加相同內容
    result2 = dedup.add_document_with_deduplication(
        test_content,
        test_metadata.copy(),
        "test_doc_2"
    )
    typer.echo(f"第二次添加結果: {result2}")
    
    # 檢查集合中的文檔數量
    results = test_collection.get(include=['documents', 'metadatas'])
    typer.echo(f"集合中總共有 {len(results['ids'])} 個文檔")
    
    # 清理測試集合
    try:
        dedup.client.delete_collection(name="test_collection")
    except:
        pass

@app.command()
def test_indexer():
    """測試索引器的重複處理功能"""
    typer.echo("測試索引器的重複處理功能")
    
    # 創建測試目錄和文件
    test_dir = "./test_index_data"
    os.makedirs(test_dir, exist_ok=True)
    
    # 創建測試文件
    test_file_path = os.path.join(test_dir, "test_file.txt")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("這是一個測試文件內容，用於測試索引器的重複處理功能。\n" * 10)
    
    # 創建索引器實例
    indexer = OptimizedIndexer()
    
    # 測試索引
    try:
        indexer.index(test_dir)
        typer.echo("索引測試完成")
    except Exception as e:
        typer.echo(f"索引測試失敗: {e}")
    
    # 清理測試數據
    try:
        import shutil
        shutil.rmtree(test_dir)
    except:
        pass

if __name__ == "__main__":
    app()
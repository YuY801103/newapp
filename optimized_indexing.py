#!/usr/bin/env python3
"""
整合優化功能的索引腳本
"""

import typer
import chromadb
from ollama import Client
import os
import hashlib
import json
from typing import Optional
from semantic_text_splitter import TextSplitter
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
import magic
from flexible_preprocessing import FlexiblePreprocessor
from improved_deduplication import ImprovedDeduplication

app = typer.Typer()

class OptimizedIndexer:
    """優化的索引器"""
    
    def __init__(self):
        self.preprocessor = FlexiblePreprocessor()
        self.dedup = ImprovedDeduplication()
    
    def index(self, path: str):
        """
        優化的索引功能
        """
        typer.echo(f"索引路徑: {path}")
        
        # 初始化Ollama客戶端
        ollama_base_url = "http://192.168.88.99:11434"
        embedding_model = "bge-m3-gpu:latest"
        ollama_client = Client(host=ollama_base_url)
        typer.echo(f"Ollama客戶端初始化完成，模型: {embedding_model}")
        
        # 初始化ChromaDB客戶端
        db_path = "./chroma_db"
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name="knowledge_base")
        typer.echo(f"ChromaDB初始化完成: {db_path}")
        
        # 初始化文本分割器
        splitter = TextSplitter(1000)
        
        # 追蹤已索引的內容雜湊
        indexed_content_hashes = set()
        indexed_hashes_file = "./indexed_hashes.txt"
        if os.path.exists(indexed_hashes_file):
            with open(indexed_hashes_file, "r") as f:
                for line in f:
                    indexed_content_hashes.add(line.strip())
        typer.echo(f"載入 {len(indexed_content_hashes)} 個已索引的雜湊")
        
        BATCH_SIZE = 32
        current_batch_chunks = []
        current_batch_metadatas = []
        current_batch_ids = []
        
        # 初始化magic
        mime = magic.Magic(mime=True)
        
        # 遍歷目錄處理文件
        for root, _, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                typer.echo(f"處理文件: {file_path}")
                
                # 確定MIME類型
                try:
                    mime_type = mime.from_file(file_path)
                except Exception as e:
                    typer.echo(f"  警告: 無法確定MIME類型 {file_path}: {e}")
                    mime_type = "unknown"
                
                # 跳過非文本文件
                if not mime_type.startswith("text/"):
                    typer.echo(f"  跳過非文本文件 {file_path} (MIME類型: {mime_type})")
                    continue
                
                try:
                    # 讀取文件內容
                    content = ""
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # 識別程式語言
                    language_name = "Unknown"
                    try:
                        lexer = guess_lexer(content)
                        language_name = lexer.name
                    except ClassNotFound:
                        pass
                    typer.echo(f"  檢測到語言: {language_name}")
                    
                    # 智慧分塊
                    chunks = splitter.chunks(content)
                    
                    for i, chunk in enumerate(chunks):
                        # 計算內容雜湊
                        content_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
                        
                        # 檢查是否已存在
                        if content_hash in indexed_content_hashes:
                            typer.echo(f"  區塊 {i} 已索引 (內容雜湊: {content_hash})")
                            continue
                        
                        # 使用改進的重複檢測
                        if self.dedup.check_duplicate_by_hash(content_hash):
                            typer.echo(f"  區塊 {i} 已存在 (內容雜湊: {content_hash})")
                            continue
                        
                        # 基本元數據
                        metadata = {
                            "file_path": file_path,
                            "file_name": file_name,
                            "file_type": os.path.splitext(file_name)[1],
                            "chunk_index": i,
                            "content_hash": content_hash,
                            "language": language_name,
                            "mime_type": mime_type
                        }
                        
                        # 使用預處理器增強元數據
                        enhanced_metadata = self.preprocessor.preprocess_chunk(chunk, metadata)
                        
                        # 合併元數據
                        metadata.update({
                            "extracted_entities": enhanced_metadata["extracted_entities"],
                            "content_type": enhanced_metadata["content_type"],
                            "keywords": enhanced_metadata["keywords"],
                            "content_length": enhanced_metadata["content_length"]
                        })
                        
                        # 根據語言類型提取更多元數據
                        if language_name in ["Python", "C", "C++", "Java", "JavaScript", "TypeScript"]:
                            import re
                            functions = re.findall(r'(?:def|function)\s+(\w+)', chunk)
                            classes = re.findall(r'class\s+(\w+)', chunk)
                            if functions:
                                metadata["functions"] = functions
                            if classes:
                                metadata["classes"] = classes
                        
                        # 對於Markdown文件，提取標題
                        if language_name == "Markdown":
                            import re
                            headers = re.findall(r'^#{1,6}\s+(.*)', chunk, re.MULTILINE)
                            if headers:
                                metadata["headers"] = headers
                        
                        # 添加到批次
                        current_batch_chunks.append(chunk)
                        current_batch_metadatas.append(metadata)
                        current_batch_ids.append(f"{file_path}-{i}")
                        
                        if len(current_batch_chunks) >= BATCH_SIZE:
                            # 處理批次
                            typer.echo(f"  處理 {len(current_batch_chunks)} 個區塊的批次...")
                            response = ollama_client.embed(model=embedding_model, input=current_batch_chunks)
                            embeddings = response['embeddings']
                            
                            collection.add(
                                documents=current_batch_chunks,
                                embeddings=embeddings,
                                metadatas=current_batch_metadatas,
                                ids=current_batch_ids
                            )
                            
                            for hash_val in [m['content_hash'] for m in current_batch_metadatas]:
                                indexed_content_hashes.add(hash_val)
                                with open(indexed_hashes_file, "a") as f:
                                    f.write(hash_val + "\n")
                            typer.echo(f"  批次索引完成")
                            
                            # 清空批次
                            current_batch_chunks = []
                            current_batch_metadatas = []
                            current_batch_ids = []
                
                except UnicodeDecodeError as e:
                    typer.echo(f"  跳過文件 {file_path} (Unicode解碼錯誤): {e}")
                    continue
                except Exception as e:
                    typer.echo(f"處理文件錯誤 {file_path}: {e}")
        
        # 處理最後的批次
        if current_batch_chunks:
            typer.echo(f"  處理最後的 {len(current_batch_chunks)} 個區塊...")
            response = ollama_client.embed(model=embedding_model, input=current_batch_chunks)
            embeddings = response['embeddings']
            
            collection.add(
                documents=current_batch_chunks,
                embeddings=embeddings,
                metadatas=current_batch_metadatas,
                ids=current_batch_ids
            )
            
            for hash_val in [m['content_hash'] for m in current_batch_metadatas]:
                indexed_content_hashes.add(hash_val)
                with open(indexed_hashes_file, "a") as f:
                    f.write(hash_val + "\n")
            typer.echo(f"  最後批次索引完成")
        
        typer.echo(f"總共索引了 {len(indexed_content_hashes)} 個唯一區塊")

@app.command()
def index(path: str):
    """
    優化的索引命令
    """
    indexer = OptimizedIndexer()
    indexer.index(path)

if __name__ == "__main__":
    app()
import chromadb

db_path = "./chroma_db"
client = chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection(name="test_collection")

# 添加一個文檔
collection.add(
    documents=["test document 1"],
    metadatas=[{"source": "test"}],
    ids=["doc1"]
)
print("First add successful")

# 嘗試添加相同內容但不同 ID 的文檔
try:
    collection.add(
        documents=["test document 1"],
        metadatas=[{"source": "test"}],
        ids=["doc2"]
    )
    print("Second add successful - 添加了相同內容但不同 ID 的文檔")
except Exception as e:
    print(f"Caught exception: {e}")

# 嘗試添加相同 ID 的文檔
try:
    collection.add(
        documents=["test document 1"],
        metadatas=[{"source": "test"}],
        ids=["doc1"]
    )
    print("Third add successful - 這不應該發生")
except Exception as e:
    print(f"Caught exception for same ID: {e}")

# 檢查集合中的文檔數量
results = collection.get(include=['documents', 'metadatas'])
print(f"集合中總共有 {len(results['ids'])} 個文檔")

# 列出所有文檔
for i, (doc_id, doc_content, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
    print(f"文檔 {i+1}:")
    print(f"  ID: {doc_id}")
    print(f"  內容: {doc_content}")
    print(f"  元數據: {metadata}")

# 清理測試集合
client.delete_collection(name="test_collection")
import aiosqlite
import json
import uuid

class AsyncCursor:
    def __init__(self, conn, col, query, projection):
        self.conn = conn
        self.col = col
        self.query = query
        self.sort_key = None
        self.sort_dir = 1
        
    def sort(self, key, direction):
        self.sort_key = key
        self.sort_dir = direction
        return self
        
    async def to_list(self, length=1000):
        async with self.conn.execute("SELECT doc FROM docs WHERE col = ?", (self.col,)) as cur:
            rows = await cur.fetchall()
            
        results = []
        for row in rows:
            d = json.loads(row[0])
            if self._match(d, self.query):
                results.append(d)
                
        if self.sort_key:
            results.sort(key=lambda x: x.get(self.sort_key, ""), reverse=(self.sort_dir == -1))
            
        return results[:length] if length else results
        
    def _match(self, doc, query):
        if not query: return True
        for k, v in query.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v): return False
            elif doc.get(k) != v:
                return False
        return True

class Collection:
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

    async def create_index(self, *args, **kwargs):
        pass
        
    def find(self, query=None, projection=None):
        return AsyncCursor(self.conn, self.name, query or {}, projection)

    def _match(self, doc, query):
        if not query: return True
        for k, v in query.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v): return False
            elif doc.get(k) != v:
                return False
        return True

    async def count_documents(self, query):
        cursor = self.find(query)
        docs = await cursor.to_list(length=None)
        return len(docs)

    async def find_one(self, query, projection=None):
        cursor = self.find(query)
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None

    async def insert_one(self, doc):
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        else:
            doc["_id"] = str(doc["_id"])
            
        doc_str = json.dumps(doc, default=str)
        await self.conn.execute("INSERT INTO docs (col, id, doc) VALUES (?, ?, ?)", (self.name, doc["_id"], doc_str))
        await self.conn.commit()
        
        class InsertResult:
            inserted_id = doc["_id"]
        return InsertResult()

    async def update_one(self, query, update):
        doc = await self.find_one(query)
        if not doc:
            return
            
        if "$set" in update:
            for k, v in update["$set"].items():
                doc[k] = v
                
        if "$inc" in update:
            for k, v in update["$inc"].items():
                parts = k.split(".")
                curr = doc
                for p in parts[:-1]:
                    if p not in curr:
                        curr[p] = {}
                    curr = curr[p]
                last = parts[-1]
                curr[last] = curr.get(last, 0) + v
                
        doc_str = json.dumps(doc, default=str)
        await self.conn.execute("UPDATE docs SET doc = ? WHERE col = ? AND id = ?", (doc_str, self.name, doc["_id"]))
        await self.conn.commit()

    async def delete_one(self, query):
        doc = await self.find_one(query)
        if doc:
            await self.conn.execute("DELETE FROM docs WHERE col = ? AND id = ?", (self.name, doc["_id"]))
            await self.conn.commit()

    async def delete_many(self, query):
        cursor = self.find(query)
        docs = await cursor.to_list(length=None)
        for doc in docs:
            await self.conn.execute("DELETE FROM docs WHERE col = ? AND id = ?", (self.name, doc["_id"]))
        await self.conn.commit()

class AsyncMongoSQLite:
    def __init__(self, db_path="local.db"):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("CREATE TABLE IF NOT EXISTS docs (col TEXT, id TEXT, doc TEXT, PRIMARY KEY (col, id))")
        await self.conn.commit()

    def close(self):
        if self.conn:
            return self.conn.close()

    def __getattr__(self, name):
        return Collection(self.conn, name)

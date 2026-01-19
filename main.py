import os
import sys
import argparse
import datetime
import uuid

# 需要安装的库：pymongo, redis, psycopg2-binary
import pymongo
import redis
import psycopg2

def run_mongo():
    uri = os.environ.get("MONGO_URI")
    if not uri:
        print("Error: MONGO_URI is not set.")
        sys.exit(1)
    
    print("--- Starting MongoDB Keep-Alive ---")
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client.get_database("keep_alive_db") # 默认库名，可修改
        collection = db.get_collection("heartbeat")

        # 1. 插入 (Insert)
        data_id = str(uuid.uuid4())
        payload = {
            "task_id": data_id,
            "type": "keep-alive",
            "created_at": datetime.datetime.utcnow()
        }
        insert_result = collection.insert_one(payload)
        print(f"[Mongo] Inserted document ID: {insert_result.inserted_id}")

        # 2. 查询 (Query)
        query_result = collection.find_one({"task_id": data_id})
        if query_result:
            print(f"[Mongo] Queried document successfully: {query_result['task_id']}")
        else:
            raise Exception("[Mongo] Failed to query inserted document")

        # 3. 删除 (Delete)
        delete_result = collection.delete_one({"task_id": data_id})
        print(f"[Mongo] Deleted count: {delete_result.deleted_count}")
        
        client.close()
        print("--- MongoDB Success ---")
    except Exception as e:
        print(f"[Mongo] Error: {e}")
        sys.exit(1)

def run_redis():
    host = os.environ.get("REDIS_HOST")
    port = os.environ.get("REDIS_PORT", 6379)
    password = os.environ.get("REDIS_PASSWORD")
    
    if not host:
        print("Error: REDIS_HOST is not set.")
        sys.exit(1)

    print("--- Starting Redis Keep-Alive ---")
    try:
        r = redis.Redis(host=host, port=port, password=password, decode_responses=True, socket_timeout=5)
        
        ttl_seconds = 86400 # 1天

        # 1. String
        r.set("ka_string", "hello", ex=ttl_seconds)
        print("[Redis] Set String with 1 day TTL")

        # 2. List
        r.lpush("ka_list", "item1")
        r.expire("ka_list", ttl_seconds)
        print("[Redis] Set List with 1 day TTL")

        # 3. Set
        r.sadd("ka_set", "member1")
        r.expire("ka_set", ttl_seconds)
        print("[Redis] Set Set(Collection) with 1 day TTL")
        
        # 验证一下 String
        val = r.get("ka_string")
        print(f"[Redis] Verification get: {val}")
        
        r.close()
        print("--- Redis Success ---")
    except Exception as e:
        print(f"[Redis] Error: {e}")
        sys.exit(1)

def run_postgres():
    dsn = os.environ.get("PG_DSN") # 例如: postgres://user:pass@host:port/dbname
    if not dsn:
        print("Error: PG_DSN is not set.")
        sys.exit(1)

    print("--- Starting PostgreSQL Keep-Alive ---")
    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()

        # 定义简单表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS keep_alive_heartbeat (
            id SERIAL PRIMARY KEY,
            check_uuid VARCHAR(50),
            created_at TIMESTAMP
        );
        """
        cur.execute(create_table_sql)
        
        # 1. 插入 (Insert)
        check_uuid = str(uuid.uuid4())
        cur.execute("INSERT INTO keep_alive_heartbeat (check_uuid, created_at) VALUES (%s, %s)", (check_uuid, datetime.datetime.now()))
        print(f"[PG] Inserted row with UUID: {check_uuid}")

        # 2. 查询 (Query)
        cur.execute("SELECT id, check_uuid FROM keep_alive_heartbeat WHERE check_uuid = %s", (check_uuid,))
        row = cur.fetchone()
        if row:
            print(f"[PG] Queried row: ID={row[0]}")
        else:
            conn.rollback()
            raise Exception("[PG] Failed to query inserted row")

        # 3. 删除 (Delete)
        cur.execute("DELETE FROM keep_alive_heartbeat WHERE check_uuid = %s", (check_uuid,))
        print(f"[PG] Deleted row count: {cur.rowcount}")

        conn.commit()
        cur.close()
        conn.close()
        print("--- PostgreSQL Success ---")
    except Exception as e:
        print(f"[PG] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", choices=["mongo", "redis", "postgres"], required=True)
    args = parser.parse_args()

    if args.service == "mongo":
        run_mongo()
    elif args.service == "redis":
        run_redis()
    elif args.service == "postgres":
        run_postgres()

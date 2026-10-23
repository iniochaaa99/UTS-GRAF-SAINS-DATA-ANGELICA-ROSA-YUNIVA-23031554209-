import os
import sys

import pandas as pd
from tqdm import tqdm
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "angelicautsgsd")  # ganti dengan password Neo4j-mu
DATABASE = "neo4j"

CSV_FILE_PATH = os.path.join("data", "events_p1.csv")  # hanya periode P1 (training)
BATCH_SIZE = 10000
NROWS = None  # isi 50000 untuk uji coba, None untuk impor penuh

CYPHER_IMPORT = """
UNWIND $batch AS row
MERGE (v:Visitor {visitorId: row.visitorid})
MERGE (i:Item {itemId: row.itemid})

WITH v, i, row
CALL {
    WITH v, i, row
    WITH v, i, row WHERE row.event = 'view'
    CREATE (v)-[:VIEWED {timestamp: row.timestamp}]->(i)

    UNION ALL

    WITH v, i, row
    WITH v, i, row WHERE row.event = 'addtocart'
    CREATE (v)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(i)

    UNION ALL

    WITH v, i, row
    WITH v, i, row WHERE row.event = 'transaction'
    CREATE (v)-[:BOUGHT {timestamp: row.timestamp, transactionId: row.transactionid}]->(i)
}
"""


def create_constraints(session):
    session.run(
        "CREATE CONSTRAINT visitor_id IF NOT EXISTS "
        "FOR (v:Visitor) REQUIRE v.visitorId IS UNIQUE"
    )
    session.run(
        "CREATE CONSTRAINT item_id IF NOT EXISTS "
        "FOR (i:Item) REQUIRE i.itemId IS UNIQUE"
    )


def import_batch(tx, batch):
    tx.run(CYPHER_IMPORT, batch=batch)


def clean_transactionid(x):
    return "" if pd.isna(x) else str(int(x))


def main():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: File '{CSV_FILE_PATH}' tidak ditemukan!")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print("Koneksi ke Neo4j berhasil!")
    except Exception as e:
        print(f"Gagal terhubung ke database: {e}")
        sys.exit(1)

    with driver, driver.session(database=DATABASE) as session:
        if session.run("MATCH (v:Visitor) RETURN v LIMIT 1").single():
            print("Database sudah berisi data Visitor.")
            print("Kosongkan dulu dengan: MATCH (n) DETACH DELETE n;")
            sys.exit(1)

        create_constraints(session)

        print(f"Membaca data dari: {CSV_FILE_PATH}")
        if NROWS:
            total_rows = NROWS
        else:
            with open(CSV_FILE_PATH, encoding="utf-8") as f:
                total_rows = sum(1 for _ in f) - 1  # kurangi baris header
        total_chunks = total_rows // BATCH_SIZE + 1

        chunks = pd.read_csv(CSV_FILE_PATH, chunksize=BATCH_SIZE, nrows=NROWS)
        for chunk in tqdm(chunks, total=total_chunks, desc="Mengimpor Batch Data"):
            chunk["transactionid"] = chunk["transactionid"].apply(clean_transactionid)
            session.execute_write(import_batch, chunk.to_dict(orient="records"))

    print("Proses impor berhasil selesai.")


if __name__ == "__main__":
    main()
import os
import sys
import logging
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv

import logging
import time
import torch
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import torch
from neo4j import GraphDatabase

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.environ["NEO4J_PASSWORD"]
DB = os.getenv("NEO4J_DATABASE", "aegisgraph")

BATCH_SIZE = 1000

def generate_embeddings():
    logger.info(f"PyTorch Version: {torch.__version__}")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"CUDA Version: {torch.version.cuda}")
        logger.info(f"GPU Name: {torch.cuda.get_device_name(0)}")
        
    logger.info("Loading SentenceTransformer model...")
    # Use the fast, lightweight model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    logger.info(f"Actual device used by SentenceTransformer: {model.device}")
    logger.info(f"Using batch size: {BATCH_SIZE}")
    
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    with driver.session(database=DB) as session:
        # Create vector index if not exists
        logger.info("Creating vector index...")
        try:
            session.run("""
                CREATE VECTOR INDEX email_embeddings IF NOT EXISTS 
                FOR (e:Email) ON (e.embedding) 
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """)
        except Exception as e:
            logger.info(f"Vector index might already exist or error: {e}")

        # Get count of emails needing embeddings
        result = session.run("MATCH (e:Email) WHERE e.embedding IS NULL RETURN count(e) AS c")
        total = result.single()["c"]
        logger.info(f"Found {total} emails requiring embeddings.")
        
        # Removed benchmark limit for full run
        logger.info(f"Full Run Mode: Processing {total} emails on GPU.")
        
        if total == 0:
            logger.info("All emails already have embeddings!")
            return
            
        processed = 0
        start_time = time.time()
        with tqdm(total=total) as pbar:
            while processed < total:
                # Fetch batch
                # We order by elementId for stable pagination
                query = """
                MATCH (e:Email) 
                WHERE e.embedding IS NULL 
                RETURN elementId(e) AS id, e.subject AS subject, e.body AS body 
                LIMIT $limit
                """
                records = session.run(query, limit=BATCH_SIZE).data()
                
                if not records:
                    break
                    
                ids = []
                texts = []
                for r in records:
                    ids.append(r["id"])
                    # Combine subject and body for rich semantic context
                    subj = r["subject"] or ""
                    body = r["body"] or ""
                    texts.append(f"Subject: {subj}\n\nBody: {body}")
                
                # Encode (this automatically utilizes all CPU cores for PyTorch)
                embeddings = model.encode(texts, batch_size=256, convert_to_numpy=True, show_progress_bar=False)
                
                # Prepare write batch
                updates = [{"id": i, "emb": emb.tolist()} for i, emb in zip(ids, embeddings)]
                
                # Write back to Neo4j
                write_query = """
                UNWIND $updates AS update
                MATCH (e:Email) WHERE elementId(e) = update.id
                SET e.embedding = update.emb
                """
                session.run(write_query, updates=updates)
                
                processed += len(records)
                pbar.update(len(records))
                
        end_time = time.time()
        duration = end_time - start_time
        emails_per_sec = processed / duration if duration > 0 else 0
        logger.info(f"Processed: {processed} emails")
        logger.info(f"Processing speed: {emails_per_sec:.2f} emails/sec")
        
        if torch.cuda.is_available():
            mem_allocated = torch.cuda.max_memory_allocated(0) / (1024 ** 2)
            logger.info(f"Max GPU VRAM Used: {mem_allocated:.2f} MB")
                
    driver.close()
    logger.info("Embedding generation complete!")

if __name__ == "__main__":
    generate_embeddings()

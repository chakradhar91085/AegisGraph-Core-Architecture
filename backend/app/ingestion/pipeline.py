import os
import re
import hashlib
import sys
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, getaddresses
from neo4j import GraphDatabase
import spacy

class Neo4jPipeline:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
        
        self.target_cluster = {
            "richard.sanders@enron.com", "mark.haedicke@enron.com", "mark.e.haedicke@enron.com",
            "james.derrick@enron.com", "louise.kitchen@enron.com", "john.lavorato@enron.com", 
            "jeff.skilling@enron.com", "kenneth.lay@enron.com", "vince.kaminski@enron.com", 
            "j.kaminski@enron.com", "richard.causey@enron.com", "andy.fastow@enron.com", 
            "steven.kean@enron.com"
        }

    def close(self):
        self.driver.close()

    def get_fingerprint(self, sender, recipients, subject, body):
        sender = (sender or "").strip().lower()
        recipients = sorted([r.strip().lower() for r in (recipients or []) if r.strip()])
        subject = (subject or "").strip()
        body = (body or "").strip()
        fingerprint_data = f"{sender}|{','.join(recipients)}|{subject}|{body}"
        return f"enron_{hashlib.sha256(fingerprint_data.encode('utf-8')).hexdigest()[:16]}"

    def strip_quoted_text(self, text):
        markers = [
            r"-----Original Message-----",
            r"___+ Forwarded by",
            r"From: .+\nSent:",
            r"On .+ wrote:"
        ]
        pattern = re.compile("|".join(markers), re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return text[:match.start()].strip()
        return text.strip()

    def fast_extract_headers(self, filepath):
        """Read only the first 10KB of the file to extract headers quickly."""
        with open(filepath, 'rb') as f:
            head = f.read(10240)
        msg = BytesParser(policy=policy.default).parsebytes(head)
        
        participants = set()
        
        sender_hdr = msg.get('From', '')
        _, sender_email = parseaddr(sender_hdr)
        if sender_email:
            participants.add(sender_email.strip().lower())
            
        for r_type in ['To', 'Cc', 'Bcc']:
            hdr = msg.get(r_type, '')
            if hdr:
                for _, email in getaddresses([hdr]):
                    if email:
                        participants.add(email.strip().lower())
                        
        return participants

    def parse_email(self, filepath):
        with open(filepath, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            
        message_id = msg.get('Message-ID', '').strip()
        
        sender_hdr = msg.get('From', '')
        sender_name, sender_email = parseaddr(sender_hdr)
        sender_email = sender_email.strip().lower()
        
        to_hdr = msg.get('To', '')
        cc_hdr = msg.get('Cc', '')
        bcc_hdr = msg.get('Bcc', '')
        
        recipients = {'to': [], 'cc': [], 'bcc': []}
        if to_hdr:
            recipients['to'] = [{'name': name, 'email': email.strip().lower()} for name, email in getaddresses([to_hdr]) if email.strip()]
        if cc_hdr:
            recipients['cc'] = [{'name': name, 'email': email.strip().lower()} for name, email in getaddresses([cc_hdr]) if email.strip()]
        if bcc_hdr:
            recipients['bcc'] = [{'name': name, 'email': email.strip().lower()} for name, email in getaddresses([bcc_hdr]) if email.strip()]
                
        subject = msg.get('Subject', '')
        date_str = msg.get('Date', '')
        
        body = msg.get_body(preferencelist=('plain'))
        body_text = body.get_content() if body else ""
        body_text = self.strip_quoted_text(body_text)
        
        flat_recips = [r['email'] for r in recipients['to'] + recipients['cc'] + recipients['bcc']]
        canonical_id = f"enron_{hashlib.sha256(message_id.encode('utf-8')).hexdigest()[:16]}" if message_id else self.get_fingerprint(sender_email, flat_recips, subject, body_text)
        
        return {
            'email_id': canonical_id,
            'message_id': message_id,
            'sender': {'name': sender_name, 'email': sender_email},
            'recipients': recipients,
            'subject': subject,
            'sent_at': date_str,
            'body': body_text,
            'filepath': filepath
        }

    def extract_topics(self, text):
        doc = self.nlp(text[:5000])
        topics = set()
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                name = re.sub(r'\s+', ' ', ent.text.strip().strip("'\"`.,:;()[]{}*&#@!?-/\\"))
                if name and len(name) > 2:
                    topics.add(name.title())
        return list(topics)

    def normalize_subject(self, subject):
        return re.sub(r'(?i)^(re:|fw:|fwd:)\s*', '', subject).strip()

    def write_batch_to_neo4j(self, batch, subject_to_email_id):
        with self.driver.session(database="aegisgraph") as session:
            # We use individual MERGE transactions due to the dynamic nature of topics/relationships
            # In production we would use UNWIND $batch, but this is simple and robust
            for email in batch:
                norm_subj = self.normalize_subject(email['subject'])
                is_reply = bool(re.match(r'(?i)^(re:)\s*', email['subject']))
                
                # Build Email
                session.run("""
                    MERGE (e:Email {email_id: $email_id})
                    ON CREATE SET 
                        e.message_id = $msg_id,
                        e.subject = $subj,
                        e.sent_at = $date,
                        e.body = $body,
                        e.source_path = $path
                """, 
                    email_id=email['email_id'], msg_id=email['message_id'], subj=email['subject'],
                    date=email['sent_at'], body=email['body'], path=email['filepath']
                )

                # REPLY_TO Edge
                if is_reply and norm_subj in subject_to_email_id:
                    parent_id = subject_to_email_id[norm_subj]
                    session.run("""
                        MATCH (e:Email {email_id: $email_id})
                        MATCH (p:Email {email_id: $parent_id})
                        MERGE (e)-[:REPLY_TO]->(p)
                    """, email_id=email['email_id'], parent_id=parent_id)

                if norm_subj:
                    subject_to_email_id[norm_subj] = email['email_id']

                sender_email = email['sender']['email']
                sender_name = email['sender']['name']
                if sender_email:
                    session.run("""
                        MERGE (p:Person {email: $email})
                        ON CREATE SET p.name = $name
                        WITH p
                        MATCH (e:Email {email_id: $email_id})
                        MERGE (p)-[:SENT]->(e)
                    """, email=sender_email, name=sender_name, email_id=email['email_id'])

                for rec in email['recipients']['to']:
                    if rec['email']:
                        session.run("""
                            MERGE (p:Person {email: $email})
                            ON CREATE SET p.name = $name
                            WITH p
                            MATCH (e:Email {email_id: $email_id})
                            MERGE (e)-[:SENT_TO]->(p)
                        """, email=rec['email'], name=rec['name'], email_id=email['email_id'])
                        
                for rec in email['recipients']['cc']:
                    if rec['email']:
                        session.run("""
                            MERGE (p:Person {email: $email})
                            ON CREATE SET p.name = $name
                            WITH p
                            MATCH (e:Email {email_id: $email_id})
                            MERGE (e)-[:CC_TO]->(p)
                        """, email=rec['email'], name=rec['name'], email_id=email['email_id'])
                
                # Topics
                topics = self.extract_topics(email['body'])
                for topic in topics:
                    session.run("""
                        MATCH (e:Email {email_id: $email_id})
                        MERGE (t:Topic {name: $name})
                        MERGE (e)-[:DISCUSSES]->(t)
                    """, email_id=email['email_id'], name=topic)

    def ingest_emails(self, base_maildir_path):
        target_mailboxes = [
            "sanders-r", "haedicke-m", "derrick-j", "kitchen-l", 
            "lavorato-j", "skilling-j", "lay-k", "kaminski-v", "kean-s"
        ]
        
        print(f"Starting Direct Mailbox Ingestion for {len(target_mailboxes)} mailboxes.", flush=True)
        
        selected_filepaths = []
        
        for mbx in target_mailboxes:
            mbx_path = os.path.join(base_maildir_path, mbx)
            if not os.path.exists(mbx_path):
                print(f"Warning: Mailbox {mbx} not found at {mbx_path}", flush=True)
                continue
                
            for root, _, files in os.walk(mbx_path):
                for file in files:
                    filepath = os.path.abspath(os.path.join(root, file))
                    if file.endswith('.') and not filepath.endswith('.'):
                        filepath += '.'
                    if os.name == 'nt' and not filepath.startswith('\\\\?\\'):
                        filepath = '\\\\?\\' + filepath
                    selected_filepaths.append(filepath)

        print(f"\n--- DIRECT PROCESSING & BATCHED NEO4J INGESTION ---", flush=True)
        print(f"Total raw files discovered in selected mailboxes: {len(selected_filepaths)}", flush=True)
        
        subject_to_email_id = {}
        batch = []
        batch_size = 500
        emails_ingested = 0
        seen_ids = set()
        
        for idx, filepath in enumerate(selected_filepaths):
            if idx > 0 and idx % 2000 == 0:
                print(f"Deep processed {idx}/{len(selected_filepaths)} files. Unique canonical emails found: {len(seen_ids)}. Ingested: {emails_ingested}", flush=True)
                
            try:
                parsed = self.parse_email(filepath)
            except Exception as e:
                continue
                
            if parsed['email_id'] in seen_ids:
                continue
            seen_ids.add(parsed['email_id'])
            
            batch.append(parsed)
            
            if len(batch) >= batch_size:
                self.write_batch_to_neo4j(batch, subject_to_email_id)
                emails_ingested += len(batch)
                batch = []

        if batch:
            self.write_batch_to_neo4j(batch, subject_to_email_id)
            emails_ingested += len(batch)

        print("\nGraph ingestion complete!", flush=True)
        print(f"Total raw files processed: {len(selected_filepaths)}", flush=True)
        print(f"Total unique canonical emails ingested: {emails_ingested}", flush=True)
        print(f"Duplicates merged: {len(selected_filepaths) - emails_ingested}", flush=True)

        with self.driver.session(database="aegisgraph") as session:
            print("\n--- GRAPH STATISTICS ---", flush=True)
            for label in ["Person", "Email", "Topic"]:
                count = session.run(f"MATCH (n:{label}) RETURN count(n) as c").single()['c']
                print(f"{label} nodes: {count}", flush=True)
            rels = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as c")
            for record in rels:
                print(f"Relationship {record['type']}: {record['c']}", flush=True)

if __name__ == '__main__':
    pipeline = Neo4jPipeline("bolt://localhost:7687", "neo4j", "aegisgraph")
    pipeline.ingest_emails(r"C:\Major Project\Project\data\raw\enron_mail_20150507\maildir")
    pipeline.close()

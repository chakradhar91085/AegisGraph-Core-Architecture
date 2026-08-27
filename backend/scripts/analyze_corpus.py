import os
import email
from email.policy import default
import json
from collections import defaultdict

MAILDIR = r"C:\Major Project\Project\data\raw\enron_mail_20150507\maildir"
OUTPUT_FILE = r"C:\Major Project\Project\data\dataset\corpus_stats.json"

def fast_parse(filepath):
    try:
        with open(filepath, 'rb') as f:
            # We only need headers, so we can stop reading after the blank line, 
            # but for simplicity we'll just read the first 10KB.
            head = f.read(10240)
            msg = email.message_from_bytes(head, policy=default)
            
            sender = msg.get('From', '').strip() if msg.get('From') else ''
            
            # Combine To, Cc, Bcc
            recipients = []
            for header in ['To', 'Cc', 'Bcc']:
                val = msg.get(header)
                if val:
                    recipients.extend([r.strip() for r in str(val).split('\n')])
            # The above is a bit naive for multiline headers, but email.policy should help
            # Let's get them properly using msg.get_all
            recipients = []
            for header in ['To', 'Cc', 'Bcc']:
                vals = msg.get_all(header, [])
                for val in vals:
                    recipients.extend([r.strip() for r in str(val).split(',')])
            recipients = [r for r in set(recipients) if r]
            
            subject = str(msg.get('Subject', '')).strip()
            msg_id = str(msg.get('Message-ID', '')).strip()
            
            return {
                'msg_id': msg_id,
                'sender': sender,
                'recipients': recipients,
                'subject': subject
            }
    except Exception as e:
        return None

def run_analysis():
    print("Starting offline analysis of Enron corpus...")
    total_files = 0
    valid_emails = 0
    
    senders = defaultdict(int)
    recipients_count = defaultdict(int)
    pairs = defaultdict(int)
    subjects = defaultdict(int)
    
    msg_id_set = set() # For deduplication
    
    for root, _, files in os.walk(MAILDIR):
        for f_name in files:
            total_files += 1
            if total_files % 50000 == 0:
                print(f"Scanned {total_files} files...")
                
            filepath = os.path.join(root, f_name)
            # Fix trailing dot issue for Windows
            if os.name == 'nt':
                filepath = '\\\\?\\' + os.path.abspath(root) + '\\' + f_name
            else:
                filepath = os.path.abspath(filepath)
                
            parsed = fast_parse(filepath)
            if not parsed or not parsed['msg_id']:
                continue
                
            # Deduplicate based on Message-ID
            if parsed['msg_id'] in msg_id_set:
                continue
            msg_id_set.add(parsed['msg_id'])
            valid_emails += 1
            
            sender = parsed['sender']
            if sender:
                senders[sender] += 1
                
            for rec in parsed['recipients']:
                if rec:
                    recipients_count[rec] += 1
                    # Alphabetical pair to count undirected interactions
                    pair = tuple(sorted([sender, rec]))
                    pairs[f"{pair[0]} <-> {pair[1]}"] += 1
                    
            sub = parsed['subject']
            # Normalize subject slightly
            if sub:
                norm_sub = sub.lower()
                if norm_sub.startswith('re:'): norm_sub = norm_sub[3:].strip()
                if norm_sub.startswith('fw:'): norm_sub = norm_sub[3:].strip()
                if norm_sub.startswith('fwd:'): norm_sub = norm_sub[4:].strip()
                if norm_sub:
                    subjects[norm_sub] += 1

    print(f"\nAnalysis complete. Total files: {total_files}, Unique Emails: {valid_emails}")
    
    # Get top 100
    top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:100]
    top_recipients = sorted(recipients_count.items(), key=lambda x: x[1], reverse=True)[:100]
    top_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:100]
    top_subjects = sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:100]
    
    stats = {
        'total_files': total_files,
        'unique_emails': valid_emails,
        'top_senders': top_senders,
        'top_recipients': top_recipients,
        'top_pairs': top_pairs,
        'top_subjects': top_subjects
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Stats written to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_analysis()

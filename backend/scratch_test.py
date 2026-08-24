import urllib.request
import json
req = urllib.request.Request(
    'http://localhost:8001/api/v1/chat',
    method='POST',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'query': 'Who does veronica.espinoza@enron.com communicate with most frequently?'}).encode('utf-8')
)
try:
  with urllib.request.urlopen(req) as response:
    raw_response = response.read().decode('utf-8')
    print("RAW RESPONSE SNIPPET:", raw_response[:200])
    data = json.loads(raw_response)
    print(f"INTENT: {data.get('intent')}")
    print(f"RESULT COUNT: {data.get('retrieval', {}).get('result_count')}")
    print(f"GRAPH DATA EXISTS: {'graph_data' in data}")
    if data.get("graph_data"):
        nodes = data["graph_data"].get("nodes", [])
        edges = data["graph_data"].get("edges", [])
        print(f"NODES: {len(nodes)}")
        print(f"EDGES: {len(edges)}")
        print(json.dumps(data["graph_data"], indent=2)[:500])
    else:
        print("GRAPH DATA IS EMPTY OR NONE")
except Exception as e:
  print('Error:', e)

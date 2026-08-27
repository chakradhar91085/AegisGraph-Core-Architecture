"""
AegisGraph Phase 11B - Safe Graph Projection Layer
Extracts visualization payload strictly from already-authorized RetrievalResponse data.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.retrieval.schemas import RetrievalResponse, ResolutionStatus

class GraphNode(BaseModel):
    id: str
    label: str
    type: str

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    weight: Optional[float] = None

class GraphVisualizationPayload(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# A safe cap to ensure UI doesn't crash on very dense clusters even if policy allows them
VISUALIZATION_CAP = 25

class GraphDataExtractor:
    def extract(self, response: RetrievalResponse) -> GraphVisualizationPayload:
        nodes = []
        edges = []

        if not response.results or response.result_count == 0:
            return GraphVisualizationPayload(nodes=[], edges=[])
            
        strategy = response.strategy
        results = response.results[:VISUALIZATION_CAP]
        
        if strategy == "employee_lookup":
            source_emp = self._get_source_entity(response)
            if source_emp:
                nodes.append(GraphNode(id=source_emp["id"], label=source_emp["name"], type="Person"))

        elif strategy == "sent_emails" or strategy == "received_emails":
            source_emp = self._get_source_entity(response)
            if source_emp:
                nodes.append(GraphNode(id=source_emp["id"], label=source_emp["name"], type="Person"))
                for row in results:
                    target_id = str(row.get("email_id") or "unknown_email_id")
                    target_label = str(row.get("subject") or "No Subject")
                    nodes.append(GraphNode(id=target_id, label=target_label, type="Email"))
                    
                    rel_type = "SENT" if strategy == "sent_emails" else "SENT_TO"
                    edges.append(GraphEdge(
                        source=source_emp["id"] if strategy == "sent_emails" else target_id, 
                        target=target_id if strategy == "sent_emails" else source_emp["id"], 
                        type=rel_type
                    ))

        elif strategy == "frequent_communication":
            source_emp = self._get_source_entity(response)
            if source_emp:
                nodes.append(GraphNode(id=source_emp["id"], label=source_emp["name"], type="Person"))
                for row in results:
                    target_id = str(row.get("email") or "unknown_email")
                    target_name = str(row.get("name") or target_id)
                    nodes.append(GraphNode(id=target_id, label=target_name, type="Person"))
                    edges.append(GraphEdge(
                        source=source_emp["id"], 
                        target=target_id, 
                        type="COMMUNICATES_FREQUENTLY_WITH", 
                        weight=float(row.get("email_count") or 1)
                    ))
                    
        elif strategy == "topical_footprint":
            source_emp = self._get_source_entity(response)
            if source_emp:
                nodes.append(GraphNode(id=source_emp["id"], label=source_emp["name"], type="Person"))
                for row in results:
                    target_id = str(row.get("topic_name") or "unknown_topic")
                    nodes.append(GraphNode(id=target_id, label=target_id, type="Topic"))
                    edges.append(GraphEdge(
                        source=source_emp["id"], 
                        target=target_id, 
                        type="DISCUSSES", 
                        weight=float(row.get("count") or 1)
                    ))
                    
        elif strategy == "person_connection":
            # For a path, we have path_names and path_weights. 
            for row in results:
                names = row.get("path_names", [])
                weights = row.get("path_weights", [])
                for name in names:
                    if not any(n.id == name for n in nodes):
                        nodes.append(GraphNode(id=name, label=name, type="Person"))
                for i in range(len(names) - 1):
                    source = names[i]
                    target = names[i+1]
                    weight = weights[i] if i < len(weights) else None
                    edges.append(GraphEdge(
                        source=source,
                        target=target,
                        type="COMMUNICATES_FREQUENTLY_WITH",
                        weight=weight
                    ))
        
        # Deduplicate nodes and edges just in case
        unique_nodes = list({n.id: n for n in nodes}.values())
        unique_edges_set = set()
        unique_edges = []
        for e in edges:
            sig = (e.source, e.target, e.type)
            if sig not in unique_edges_set:
                unique_edges_set.add(sig)
                unique_edges.append(e)

        return GraphVisualizationPayload(nodes=unique_nodes, edges=unique_edges)

    def _get_source_entity(self, response: RetrievalResponse) -> Optional[Dict[str, str]]:
        if response.resolved_entities:
            for entity in response.resolved_entities:
                if entity.status == ResolutionStatus.FOUND and entity.matches:
                    match = entity.matches[0]
                    # We need a stable ID. We'll prefer email first, then fallback to name or query_value.
                    ent_id = match.get("email") or match.get("name") or entity.query_value
                    name = match.get("name") or entity.query_value
                    
                    return {
                        "id": str(ent_id) if ent_id else "unknown_id", 
                        "name": str(name) if name else "Unknown Person"
                    }
        return None

graph_extractor = GraphDataExtractor()

import pytest
from app.retrieval.graph_extractor import graph_extractor, GraphVisualizationPayload
from app.retrieval.schemas import RetrievalResponse, ResolvedEntity, ResolutionStatus

def test_frequent_communication_extraction():
    # Setup mock response
    resolved = ResolvedEntity(
        type="employee",
        query_value="veronica",
        status=ResolutionStatus.FOUND,
        matches=[{"employee_id": "emp_123", "name": "Veronica Espinoza"}]
    )
    
    response = RetrievalResponse(
        query="Who does veronica communicate with?",
        intent="frequent_communication",
        resolved_entities=[resolved],
        results=[
            {"employee_id": "emp_456", "name": "Russell Diamond", "weight": 139},
            {"employee_id": "emp_789", "name": "John Doe", "weight": 50}
        ],
        result_count=2,
        strategy="frequent_communication"
    )
    
    payload = graph_extractor.extract(response)
    
    # Assert nodes
    assert len(payload.nodes) == 3
    node_ids = {n.id for n in payload.nodes}
    assert "emp_123" in node_ids
    assert "emp_456" in node_ids
    assert "emp_789" in node_ids
    
    # Assert edges
    assert len(payload.edges) == 2
    for e in payload.edges:
        assert e.source == "emp_123"
        assert e.type == "COMMUNICATES_FREQUENTLY_WITH"
        assert e.weight in [139, 50]

def test_person_connection_extraction():
    resolved1 = ResolvedEntity(
        type="employee",
        query_value="john",
        status=ResolutionStatus.FOUND,
        matches=[{"employee_id": "emp_1", "name": "John"}]
    )
    resolved2 = ResolvedEntity(
        type="employee",
        query_value="jane",
        status=ResolutionStatus.FOUND,
        matches=[{"employee_id": "emp_2", "name": "Jane"}]
    )
    
    response = RetrievalResponse(
        query="connection between john and jane",
        intent="person_connection",
        resolved_entities=[resolved1, resolved2],
        results=[
            {"path_names": ["John", "Alice", "Jane"], "path_weights": [10, 5]}
        ],
        result_count=1,
        strategy="person_connection"
    )
    
    payload = graph_extractor.extract(response)
    
    assert len(payload.nodes) == 3
    assert len(payload.edges) == 2
    
    edge1 = payload.edges[0]
    assert edge1.source == "John"
    assert edge1.target == "Alice"
    assert edge1.weight == 10
    
    edge2 = payload.edges[1]
    assert edge2.source == "Alice"
    assert edge2.target == "Jane"
    assert edge2.weight == 5

def test_blocked_or_empty_retrieval():
    response = RetrievalResponse(
        query="show emails",
        intent="sent_emails",
        results=[],
        result_count=0,
        strategy="blocked_by_policy"
    )
    
    payload = graph_extractor.extract(response)
    assert len(payload.nodes) == 0
    assert len(payload.edges) == 0

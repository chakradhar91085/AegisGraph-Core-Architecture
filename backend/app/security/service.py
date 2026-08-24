import time
import logging
from typing import Any, Dict
from app.security.models import TelemetryEvent, SignalValues, QueryRecord
from app.security.session import session_store
from app.security.embeddings import embedding_provider
from app.security.signals import signals_calculator
from app.security.risk import risk_engine
from app.security.policy import policy_engine
from app.retrieval.schemas import RetrievalResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class AegisSecurityService:
    async def observe_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Step 1: Pre-retrieval observation.
        Fetches embedding, calculates semantic drift, returns partial context.
        """
        current_time = time.time()
        
        # Cleanup old history based on temporal window
        session_store.cleanup_old_history(session_id, current_time)
        
        # Fetch current embedding
        current_embedding = await embedding_provider.get_embedding(query)
        
        # Get previous query for semantic drift
        prev_record = session_store.get_previous_query(session_id)
        prev_embedding = prev_record.embedding if prev_record else None
        
        # Calculate Semantic Drift
        if prev_embedding and current_embedding:
            semantic_drift = signals_calculator.calculate_semantic_drift(current_embedding, prev_embedding)
        else:
            semantic_drift = 0.0
            
        # Calculate Adaptive Policy based on the smoothed risk BEFORE this query
        state = session_store.get_or_create_session(session_id)
        current_policy = policy_engine.calculate_policy(state.last_smoothed_risk)
            
        return {
            "session_id": session_id,
            "query": query,
            "timestamp": current_time,
            "embedding": current_embedding,
            "semantic_drift": semantic_drift,
            "policy": current_policy
        }

    async def calculate_risk(self, ctx: Dict[str, Any], retrieval_response: RetrievalResponse) -> TelemetryEvent:
        """
        Step 2: Post-retrieval observation.
        Calculates remaining signals (temporal, entity, graph), fuses risk, and updates session.
        """
        session_id = ctx["session_id"]
        current_time = ctx["timestamp"]
        
        # Extract entities from retrieval response (if applicable)
        # We need to map the resolved query entities into the context.
        # But wait, retrieval_response doesn't expose the resolved entities directly,
        # it just exposes `intent` and `strategy` and `results`.
        # However, we can use the `query` text or `intent` to approximate, or if the intent was employee_lookup, 
        # we can extract the employee name from the results.
        # Actually, Phase 2 entity_resolver is what extracted entities.
        # For Phase 4A, let's extract words from the query that look like entities or use the results.
        # To keep it completely isolated, we will just use the intent and results. 
        # If it's employee_lookup, the entity is the name in the first result.
        
        entities = []
        if retrieval_response.results:
            if retrieval_response.strategy == "employee_lookup":
                entities.append(retrieval_response.results[0].get("name", ctx["query"]))
            elif retrieval_response.strategy in ("sent_emails", "received_emails"):
                # The entity is the employee whose emails we are fetching.
                # In phase 2, we don't have the employee name in the email result directly, but it's part of the intent.
                # Let's just use the query string as a proxy for the entity if we can't extract it cleanly.
                entities.append(ctx["query"])
            elif retrieval_response.strategy == "chunk_entities":
                # The entities are the actual entities returned
                for row in retrieval_response.results:
                    entities.append(row.get("entity_name", ""))
            elif retrieval_response.strategy == "entity_relationships":
                for row in retrieval_response.results:
                    entities.append(row.get("entity_name", ""))
                    
        # Filter out empty entities
        entities = [e for e in entities if e]
        
        # Get history for temporal and entity calculations
        state = session_store.get_or_create_session(session_id)
        # History currently does NOT include the CURRENT query yet.
        history = [q for q in state.history if q.timestamp >= (current_time - settings.SECURITY_TEMPORAL_WINDOW_SECONDS)]
        
        # Calculate Temporal Frequency using the new delta_tau exponential decay model
        temporal_frequency = signals_calculator.calculate_temporal_frequency(history, current_time)
        
        # Calculate Entity Focus (including current query's entities)
        # Create a temporary history list adding the current record
        temp_history = history + [QueryRecord(timestamp=current_time, query=ctx["query"], entities=entities)]
        entity_focus = signals_calculator.calculate_entity_focus(temp_history)
        
        # Calculate Graph Footprint
        graph_footprint = signals_calculator.calculate_graph_footprint(
            intent=retrieval_response.intent,
            result_count=retrieval_response.result_count
        )
        
        signals = SignalValues(
            semantic_drift=ctx["semantic_drift"],
            temporal_frequency=temporal_frequency,
            entity_focus=entity_focus,
            graph_footprint=graph_footprint
        )
        
        # Fuse Risk
        instantaneous_risk = risk_engine.calculate_instantaneous_risk(signals)
        
        # EWMA Smoothing
        prev_smoothed = state.last_smoothed_risk
        smoothed_risk = risk_engine.calculate_ewma(instantaneous_risk, prev_smoothed)
        
        # Persist to Session Store
        record = QueryRecord(
            timestamp=current_time,
            query=ctx["query"],
            embedding=ctx["embedding"],
            entities=entities
        )
        session_store.add_query_record(session_id, record)
        session_store.update_smoothed_risk(session_id, smoothed_risk)
        
        # Return Telemetry
        return TelemetryEvent(
            session_id=session_id,
            timestamp=current_time,
            query=ctx["query"],
            intent=retrieval_response.intent,
            retrieval_strategy=retrieval_response.strategy,
            result_count=retrieval_response.result_count,
            signals=signals,
            instantaneous_risk=instantaneous_risk,
            smoothed_risk=smoothed_risk,
            policy=ctx["policy"],
            blocked_by_policy=(retrieval_response.strategy == "blocked_by_policy")
        )

# Singleton
aegis_security = AegisSecurityService()

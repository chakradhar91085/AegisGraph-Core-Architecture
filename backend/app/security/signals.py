import math
from typing import List
from app.core.config import settings
from app.security.models import QueryRecord
import logging

logger = logging.getLogger(__name__)

class Signals:
    @staticmethod
    def calculate_semantic_drift(current_emb: List[float], prev_emb: List[float]) -> float:
        """
        S_sem(t) = 1 - cos(E_t, E_{t-1})
        Assumes embeddings are already L2 normalized, so cos is just dot product.
        Returns 0.0 on missing embedding.
        """
        if not current_emb or not prev_emb:
            return 0.0
            
        if len(current_emb) != len(prev_emb):
            return 0.0
            
        dot_product = sum(c * p for c, p in zip(current_emb, prev_emb))
        
        # Clamp dot_product to [-1.0, 1.0] due to floating point inaccuracies
        dot_product = max(-1.0, min(1.0, dot_product))
        
        drift = 1.0 - dot_product
        return float(max(0.0, min(1.0, drift))) # Strictly bounded to [0,1] without division. Negative cosine similarity will clip at 1.0.

    @staticmethod
    def calculate_temporal_frequency(history: List[QueryRecord], current_time: float) -> float:
        """
        S_temp(t) = min(1, N_t / tau)
        history should only contain queries within the time window.
        """
        if not history:
            return 0.0
            
        # Get the previous query from history (since history does NOT contain current_time yet)
        # Assuming the history contains previous queries in chronological order
        # Wait, if history is empty, we return 0.0. The history passed in here is the trailing 60s window,
        # but it might be empty if this is the first query in the session.
        if len(history) == 0:
            return 0.0
            
        prev_time = history[-1].timestamp
        delta_tau = current_time - prev_time
        
        if delta_tau < 0.0:
            delta_tau = 0.0
            
        alpha_temp = settings.SECURITY_ALPHA_TEMP
        S_temp = math.exp(-alpha_temp * delta_tau)
        
        return float(max(0.0, min(1.0, S_temp)))

    @staticmethod
    def calculate_entity_focus(history: List[QueryRecord]) -> float:
        """
        S_ent(t) = 1 - H(E_t) / log(|E_t| + epsilon)
        H is entropy.
        """
        # Collect all entities in the window
        all_entities = []
        for rec in history:
            all_entities.extend(rec.entities)
            
        if len(all_entities) < 2:
            return 0.0 # Insufficient history for entity concentration
            
        unique_entities = set(all_entities)
        
        # If exactly 1 unique entity, entropy is 0, so focus is 1.0
        if len(unique_entities) == 1:
            return 1.0
            
        # Calculate entropy
        total = float(len(all_entities))
        entropy = 0.0
        for e in unique_entities:
            p = all_entities.count(e) / total
            if p > 0:
                entropy -= p * math.log(p)
                
        # Normalize
        epsilon = 1e-9
        max_entropy = math.log(len(unique_entities) + epsilon)
        
        if max_entropy <= 0:
            return 1.0
            
        focus = 1.0 - (entropy / max_entropy)
        return float(max(0.0, min(1.0, focus)))

    @staticmethod
    def calculate_graph_footprint(intent: str, result_count: int) -> float:
        """
        S_graph(t) = min(1, d_t / d_max + eta * v_t / v_max)
        """
        if result_count == 0:
            return 0.0
            
        depth_map = {
            "employee_lookup": 1,
            "received_emails": 2,
            "sent_emails": 2,
            "email_chunks": 3,
            "chunk_entities": 4,
            "entity_relationships": 5
        }
        
        d_t = depth_map.get(intent, 0)
        v_t = result_count
        
        d_max = float(settings.SECURITY_GRAPH_MAX_DEPTH)
        v_max = float(settings.SECURITY_GRAPH_MAX_NODES)
        eta = settings.SECURITY_GRAPH_WEIGHT
        
        if d_max <= 0 or v_max <= 0:
            return 0.0
            
        depth_term = d_t / d_max
        volume_term = eta * (v_t / v_max)
        
        val = depth_term + volume_term
        return float(max(0.0, min(1.0, val)))

signals_calculator = Signals()

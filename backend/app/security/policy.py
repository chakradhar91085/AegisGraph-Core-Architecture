import math
from app.core.config import settings
from app.security.models import AdaptivePolicy, RiskLevel

class PolicyEngine:
    @staticmethod
    def calculate_policy(ewma_risk: float) -> AdaptivePolicy:
        """
        Calculate adaptive response policy parameters based on the smoothed risk score (Gamma_bar_t).
        
        kappa_t = 1 - 1 / (1 + exp(-theta_slope * (Gamma_bar_t - theta_mid)))
        k_eff = max(1, floor(kappa_t * k_baseline))
        d_eff = max(0, floor(kappa_t * d_baseline))
        """
        theta_mid = settings.SECURITY_THETA_MID
        theta_slope = settings.SECURITY_THETA_SLOPE
        
        # Determine discrete risk level
        if ewma_risk < 0.3:
            level = RiskLevel.LOW
        elif ewma_risk < 0.7:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.HIGH
            
        # Calculate attenuation factor (kappa_t) using sigmoid
        # If risk == theta_mid, exponent is 0, exp(0) = 1, 1/(1+1) = 0.5, kappa_t = 0.5
        # If risk > theta_mid, exponent is negative, exp goes to 0, 1/(1+0) = 1, kappa_t goes to 0
        exponent = -theta_slope * (ewma_risk - theta_mid)
        
        # Prevent math overflow if exponent is extremely large (though ewma_risk is bounded 0-1)
        try:
            sigmoid_val = 1.0 / (1.0 + math.exp(exponent))
        except OverflowError:
            sigmoid_val = 0.0 if exponent > 0 else 1.0
            
        kappa_t = 1.0 - sigmoid_val
        
        # Clamp attenuation factor safely
        kappa_t = float(max(0.0, min(1.0, kappa_t)))
        
        # Baselines are taken from current configuration limits
        k_baseline = float(settings.MAX_RECORDS)
        d_baseline = float(settings.SECURITY_GRAPH_MAX_DEPTH)
        
        # Effective constraints
        k_eff = max(1, math.floor(kappa_t * k_baseline))
        d_eff = max(0, math.floor(kappa_t * d_baseline))
        
        return AdaptivePolicy(
            risk_score=ewma_risk,
            risk_level=level,
            attenuation_factor=kappa_t,
            effective_context_limit=k_eff,
            effective_graph_depth=d_eff
        )

policy_engine = PolicyEngine()

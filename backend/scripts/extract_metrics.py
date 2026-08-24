import json

data = json.load(open('scripts/phase4d_evaluation.json'))

for sc in ['G_SUSTAINED_RAPID_ENTITY_FOCUSED', 'H_SUSTAINED_MULTI_VECTOR_GRAPH']:
    print(f'\n=== {sc} ===')
    ag = data['AEGISGRAPH'][sc]
    bl = data['BASELINE'][sc]
    max_ewma = max(r['EWMA_risk'] for r in ag)
    first_med = next((r['query_number'] for r in ag if r['risk_level'] == 'MEDIUM'), 'N/A')
    first_high = next((r['query_number'] for r in ag if r['risk_level'] == 'HIGH'), 'N/A')
    blocked = sum(1 for r in ag if r['blocked_by_policy'])
    bl_total = sum(r['records_passed_to_context_builder'] for r in bl)
    ag_total = sum(r['records_passed_to_context_builder'] for r in ag)
    reduction = (bl_total - ag_total) / bl_total * 100 if bl_total > 0 else 0
    print(f'  Max EWMA: {max_ewma:.4f}')
    print(f'  First MEDIUM: Q{first_med}')
    print(f'  First HIGH: Q{first_high}')
    print(f'  Blocked queries: {blocked}')
    print(f'  Baseline exposure: {bl_total}')
    print(f'  AegisGraph exposure: {ag_total}')
    print(f'  Reduction: {reduction:.1f}%')
    
    print('\n  Query-by-query AegisGraph telemetry:')
    print(f'  {"Q#":>3} {"EWMA":>7} {"Level":>6} {"Atten":>7} {"CtxLim":>6} {"Depth":>5} {"Exposed":>7} {"Blocked":>7}')
    for r in ag:
        print(f'  {r["query_number"]:>3} {r["EWMA_risk"]:>7.4f} {r["risk_level"]:>6} {r["attenuation_factor"]:>7.4f} {r["effective_context_limit"]:>6} {r["effective_graph_depth"]:>5} {r["records_passed_to_context_builder"]:>7} {str(r["blocked_by_policy"]):>7}')

# Overall totals
print('\n=== OVERALL TOTALS ===')
bl_total = sum(r['records_passed_to_context_builder'] for s in data['BASELINE'].values() for r in s)
ag_total = sum(r['records_passed_to_context_builder'] for s in data['AEGISGRAPH'].values() for r in s)
print(f'Baseline total: {bl_total}')
print(f'AegisGraph total: {ag_total}')
print(f'Reduction: {(bl_total - ag_total) / bl_total * 100:.1f}%')

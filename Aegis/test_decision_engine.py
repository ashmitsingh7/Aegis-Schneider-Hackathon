from decision_engine.optimizer import create_decision_intelligence_engine

# Create decision engine
engine = create_decision_intelligence_engine()

# Test case: degrading transformer
asset_condition = {
    'health_score': 65,
    'failure_probability': 0.30,
    'rul_days': 45,
    'load_percent': 89,
    'winding_temp_c': 84.0
}

result = engine.evaluate_all_interventions(asset_condition)

print('Decision Engine Test:')
print('Recommended Action:', result['recommendation'])
print('Recommendation Score:', '{:.2f}'.format(result['recommended_score']))
print('')
print('Top 3 Options:')
sorted_options = sorted(result['interventions'].items(), key=lambda x: x[1]['decision_score'])[:3]
for intervention, eval_result in sorted_options:
    print('  {}: {:.2f} (Risk: {:.1f}, Cost: ${:.0f}, Life: {:.0f}days)'.format(
        intervention, eval_result['decision_score'],
        eval_result['risk_score'], eval_result['cost_usd'],
        eval_result['life_impact_days']))
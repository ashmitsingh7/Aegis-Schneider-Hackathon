from decision_engine.optimizer import create_decision_intelligence_engine

# Create decision engine
engine = create_decision_intelligence_engine()

# Test case: clearly degrading transformer that should trigger load reduction
asset_condition = {
    'health_score': 60,
    'failure_probability': 0.40,  # Higher failure probability
    'rul_days': 30,
    'load_percent': 92,           # Very high load
    'winding_temp_c': 88          # High winding temperature
}

result = engine.evaluate_all_interventions(asset_condition)

print('Decision Engine Test - Clear Degradation Case:')
print('Recommended Action:', result['recommendation'])
print('Recommendation Score:', '{:.2f}'.format(result['recommended_score']))
print('')
print('All Options:')
sorted_options = sorted(result['interventions'].items(), key=lambda x: x[1]['decision_score'])
for intervention, eval_result in sorted_options:
    print('  {}: {:.2f} (Risk: {:.1f}, Cost: ${:.0f}, Life: {:.0f}days)'.format(
        intervention, eval_result['decision_score'],
        eval_result['risk_score'], eval_result['cost_usd'],
        eval_result['life_impact_days']))

    # Show reasoning for top option
    if intervention == result['recommendation']:
        print('      Reasoning:')
        for reason in eval_result['reasoning'][:3]:
            print('        -', reason)
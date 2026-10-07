PYTHONPATH=/home/singh/Aegis/backend python3 -c "
from decision_engine.optimizer import create_decision_intelligence_engine
engine = create_decision_intelligence_engine()
print('Current weights:', engine.get_weights())
"
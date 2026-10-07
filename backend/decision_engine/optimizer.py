"""
Decision Intelligence Optimizer for Aegis
Evaluates intervention strategies using multi-criteria decision analysis to recommend optimal actions
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
import logging
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformerDecisionOptimizer:
    """
    Decision intelligence optimizer for power transformer interventions
    Evaluates multiple intervention strategies using weighted criteria to recommend optimal action
    """

    def __init__(self):
        """Initialize the decision optimizer"""
        # Default weights for decision criteria (can be made configurable)
        # Based on the project plan: 40% risk, 25% cost, 20% downtime, 15% life impact
        self.criteria_weights = {
            'risk': 0.40,      # Risk of failure or damage
            'cost': 0.25,      # Financial cost of intervention
            'downtime': 0.20,  # Service downtime/interruption
            'life_impact': 0.15 # Impact on remaining useful life
        }

        # Intervention strategies as defined in the project plan
        self.intervention_strategies = {
            'CONTINUE_OPERATION': {
                'name': 'Continue Operation',
                'description': 'Continue operating at current levels with increased monitoring',
                'base_cost': 0,                    # No direct financial cost
                'base_downtime_hours': 0,          # No service interruption
                'life_impact_factor': 1.0,         # Neutral impact on life (baseline)
                'risk_multiplier': 1.0             # Baseline risk
            },
            'REDUCE_LOAD': {
                'name': 'Reduce Load',
                'description': 'Reduce electrical loading to decrease thermal stress',
                'base_cost': 500,                  # Minor operational cost
                'base_downtime_hours': 0,          # Typically no downtime for load reduction
                'life_impact_factor': 1.2,         # Positive impact - extends life
                'risk_multiplier': 0.6             # Significant risk reduction
            },
            'SCHEDULE_MAINTENANCE': {
                'name': 'Schedule Maintenance',
                'description': 'Plan maintenance intervention for near future',
                'base_cost': 5000,                 # Moderate maintenance cost
                'base_downtime_hours': 4,          # Short planned outage
                'life_impact_factor': 1.5,         # Strong positive impact
                'risk_multiplier': 0.4             # Good risk reduction
            },
            'REPLACE_ASSET': {
                'name': 'Replace Asset',
                'description': 'Replace the transformer with a new unit',
                'base_cost': 50000,                # High replacement cost
                'base_downtime_hours': 24,         # Significant service interruption
                'life_impact_factor': 2.0,         # Maximum life impact (new asset)
                'risk_multiplier': 0.1             # Minimal risk (new equipment)
            }
        }

        # Risk level to numeric score mapping (0-100 scale, lower is better)
        self.risk_level_mapping = {
            'MINIMAL': 10,
            'LOW': 25,
            'MEDIUM': 50,
            'HIGH': 75,
            'CRITICAL': 90
        }

        logger.info("Transformer Decision Optimizer initialized")

    def evaluate_interventions(self, telemetry_data: Dict[str, Any],
                             health_metrics: Dict[str, Any] = None,
                             rul_metrics: Dict[str, Any] = None,
                             risk_assessment: Dict[str, Any] = None,
                             simulation_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate all intervention strategies and recommend optimal action

        Args:
            telemetry_data: Current telemetry readings
            health_metrics: Health assessment from health model (optional)
            rul_metrics: RUL assessment from RUL model (optional)
            risk_assessment: Risk assessment from risk model (optional)
            simulation_results: Digital twin simulation results for what-if analysis (optional)

        Returns:
            Dictionary with intervention scores, recommendation, and explanation
        """
        try:
            # Get baseline risk assessment if not provided
            if risk_assessment is None:
                # In a real implementation, we would call the risk model here
                # For now, derive basic risk from available data
                risk_level = health_metrics.get('risk_level', 'MEDIUM') if health_metrics else 'MEDIUM'
                baseline_risk_score = self.risk_level_mapping.get(risk_level, 50)
            else:
                baseline_risk_score = risk_assessment.get('overall_risk_score', 3.0) * 20  # Convert 0-5 to 0-100 scale

            # Evaluate each intervention strategy
            intervention_evaluations = {}

            for strategy_key, strategy_info in self.intervention_strategies.items():
                evaluation = self._evaluate_single_intervention(
                    strategy_key, strategy_info,
                    telemetry_data, health_metrics, rul_metrics,
                    risk_assessment, simulation_results, baseline_risk_score
                )
                intervention_evaluations[strategy_key] = evaluation

            # Find the optimal intervention (lowest score is best)
            optimal_strategy = min(intervention_evaluations.keys(),
                                 key=lambda k: intervention_evaluations[k]['total_score'])

            # Generate explanation for the recommendation
            explanation = self._generate_explanation(
                optimal_strategy, intervention_evaluations,
                telemetry_data, health_metrics, rul_metrics,
                risk_assessment, simulation_results
            )

            # Prepare result
            optimal_evaluation = intervention_evaluations[optimal_strategy]

            result = {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'recommended_intervention': self.intervention_strategies[optimal_strategy]['name'],
                'recommended_intervention_key': optimal_strategy,
                'intervention_scores': {
                    key: {
                        'name': info['name'],
                        'total_score': round(eval_data['total_score'], 1),
                        'risk_score': round(eval_data['risk_score'], 1),
                        'cost_score': round(eval_data['cost_score'], 1),
                        'downtime_score': round(eval_data['downtime_score'], 1),
                        'life_impact_score': round(eval_data['life_impact_score'], 1),
                        'breakdown': eval_data['breakdown']
                    }
                    for key, (info, eval_data) in zip(
                        self.intervention_strategies.keys(),
                        intervention_evaluations.items()
                    )
                },
                'optimal_intervention_score': round(optimal_evaluation['total_score'], 1),
                'explanation': explanation,
                'assessment_details': {
                    'timestamp': pd.Timestamp.now().isoformat(),
                    'criteria_weights': self.criteria_weights.copy(),
                    'baseline_risk_score': round(baseline_risk_score, 1),
                    'health_score': health_metrics.get('health_score', 50) if health_metrics else 50,
                    'rul_years': rul_metrics.get('rul_years', 25) if rul_metrics else 25,
                    'risk_level': risk_assessment.get('overall_risk_level', 'MEDIUM') if risk_assessment else 'MEDIUM'
                }
            }

            logger.info(f"Decision optimization completed: {result['recommended_intervention']} "
                       f"(score: {result['optimal_intervention_score']})")
            return result

        except Exception as e:
            logger.error(f"Error in decision optimization: {e}")
            # Return safe default recommendation
            return self._get_default_recommendation(telemetry_data)

    def _evaluate_single_intervention(self, strategy_key: str, strategy_info: Dict[str, Any],
                                    telemetry_data: Dict[str, Any],
                                    health_metrics: Dict[str, Any] = None,
                                    rul_metrics: Dict[str, Any] = None,
                                    risk_assessment: Dict[str, Any] = None,
                                    simulation_results: Dict[str, Any] = None,
                                    baseline_risk_score: float = 50.0) -> Dict[str, Any]:
        """
        Evaluate a single intervention strategy across all decision criteria
        """
        # Get base values from strategy definition
        base_cost = strategy_info['base_cost']
        base_downtime_hours = strategy_info['base_downtime_hours']
        life_impact_factor = strategy_info['life_impact_factor']
        risk_multiplier = strategy_info['risk_multiplier']

        # Calculate risk score for this intervention
        # Lower score = better (less risk)
        if risk_assessment:
            # Use provided risk assessment, adjusted by intervention
            baseline_risk = risk_assessment.get('overall_risk_score', 3.0) * 20  # 0-5 to 0-100
        else:
            baseline_risk = baseline_risk_score

        intervention_risk = baseline_risk * risk_multiplier

        # Apply additional risk modifiers based on intervention specifics
        risk_adjustment = self._calculate_risk_adjustment(
            strategy_key, telemetry_data, health_metrics, simulation_results
        )
        final_risk_score = max(0, min(100, intervention_risk + risk_adjustment))

        # Calculate cost score
        # Normalize cost to 0-100 scale (where 0 is best/no cost, 100 is worst)
        # Assuming maximum reasonable cost of $100,000 for extreme interventions
        max_reasonable_cost = 100000
        cost_score = min(100, (base_cost / max_reasonable_cost) * 100)

        # Calculate downtime score
        # Normalize downtime to 0-100 scale (where 0 is best, 100 is worst)
        # Assuming maximum reasonable downtime of 168 hours (1 week)
        max_reasonable_downtime = 168  # 1 week in hours
        downtime_score = min(100, (base_downtime_hours / max_reasonable_downtime) * 100)

        # Calculate life impact score
        # Lower score = better (more positive life impact)
        # Life impact factor: >1.0 is positive, <1.0 is negative, 1.0 is neutral
        # Convert to 0-100 scale where 50 is neutral, <50 is good, >50 is bad
        if life_impact_factor >= 1.0:
            # Positive or neutral impact - score below 50
            life_impact_score = 50 - ((life_impact_factor - 1.0) * 25)  # 1.0=50, 2.0=25, 3.0=0
        else:
            # Negative impact - score above 50
            life_impact_score = 50 + ((1.0 - life_impact_factor) * 50)  # 1.0=50, 0.5=75, 0.0=100

        life_impact_score = max(0, min(100, life_impact_score))

        # Calculate weighted total score (lower is better)
        total_score = (
            self.criteria_weights['risk'] * final_risk_score +
            self.criteria_weights['cost'] * cost_score +
            self.criteria_weights['downtime'] * downtime_score +
            self.criteria_weights['life_impact'] * life_impact_score
        )

        # Prepare detailed breakdown for transparency
        breakdown = {
            'risk': {
                'raw_score': round(final_risk_score, 1),
                'weight': self.criteria_weights['risk'],
                'weighted_contribution': round(self.criteria_weights['risk'] * final_risk_score, 1),
                'description': f"Risk of failure/damage intervention: {strategy_info['name']}"
            },
            'cost': {
                'raw_value': base_cost,
                'raw_score': round(cost_score, 1),
                'weight': self.criteria_weights['cost'],
                'weighted_contribution': round(self.criteria_weights['cost'] * cost_score, 1),
                'description': f"Financial cost: ${base_cost:,}"
            },
            'downtime': {
                'raw_value': base_downtime_hours,
                'raw_score': round(downtime_score, 1),
                'weight': self.criteria_weights['downtime'],
                'weighted_contribution': round(self.criteria_weights['downtime'] * downtime_score, 1),
                'description': f"Service downtime: {base_downtime_hours} hours"
            },
            'life_impact': {
                'raw_value': life_impact_factor,
                'raw_score': round(life_impact_score, 1),
                'weight': self.criteria_weights['life_impact'],
                'weighted_contribution': round(self.criteria_weights['life_impact'] * life_impact_score, 1),
                'description': f"Life impact factor: {life_impact_factor}x (baseline=1.0)"
            }
        }

        return {
            'strategy_key': strategy_key,
            'strategy_name': strategy_info['name'],
            'risk_score': final_risk_score,
            'cost_score': cost_score,
            'downtime_score': downtime_score,
            'life_impact_score': life_impact_score,
            'total_score': total_score,
            'breakdown': breakdown
        }

    def _calculate_risk_adjustment(self, strategy_key: str,
                                 telemetry_data: Dict[str, Any],
                                 health_metrics: Dict[str, Any] = None,
                                 simulation_results: Dict[str, Any] = None) -> float:
        """Calculate additional risk adjustments based on intervention specifics"""
        adjustment = 0.0

        load_percent = telemetry_data.get('load_percent', 0.0)
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)

        if strategy_key == 'REDUCE_LOAD':
            # Load reduction reduces risk, especially if currently overloaded
            if load_percent > 100:
                # Proportional risk reduction based on how much overloaded
                overload_amount = load_percent - 100
                adjustment = -min(20, overload_amount * 2)  # Up to -20 points
            elif load_percent > 85:
                # Moderate reduction for high but not overloaded
                adjustment = -min(10, (load_percent - 85) * 0.7)  # Up to -10 points
            else:
                # Little benefit from reducing already moderate load
                adjustment = -2  # Small benefit

        elif strategy_key == 'SCHEDULE_MAINTENANCE':
            # Maintenance reduces risk based on current condition
            if health_metrics:
                health_score = health_metrics.get('health_score', 50)
                # Poor health gets more benefit from maintenance
                if health_score < 50:
                    adjustment = -min(15, (50 - health_score) * 0.3)  # Up to -15 points
                elif health_score < 70:
                    adjustment = -min(10, (70 - health_score) * 0.2)  # Up to -10 points
                else:
                    adjustment = -3  # Small preventive benefit
            else:
                adjustment = -5  # Default maintenance benefit

        elif strategy_key == 'REPLACE_ASSET':
            # Replacement eliminates most risks but has procedure risks
            # Base risk from replacement procedure itself
            adjustment = 5  # Small procedure risk

            # But eliminates asset-based risks
            if health_metrics:
                health_score = health_metrics.get('health_score', 50)
                # The worse the health, the more risk is eliminated by replacement
                risk_eliminated = max(0, (50 - health_score) * 0.4)  # Up to 10 points
                adjustment -= risk_eliminated

        elif strategy_key == 'CONTINUE_OPERATION':
            # Continuing operation may increase risk if already stressed
            if health_metrics:
                health_score = health_metrics.get('health_score', 50)
                if health_score < 40:  # Poor condition
                    adjustment = min(15, (40 - health_score) * 0.4)  # Up to +15 points
                elif health_score < 60:  # Fair condition
                    adjustment = min(8, (60 - health_score) * 0.2)   # Up to +8 points
            else:
                # Increase risk based on temperature and load
                if winding_temp > 95:
                    adjustment = min(10, (winding_temp - 95) * 0.2)  # Up to +10 points
                if load_percent > 110:
                    adjustment = min(10, (load_percent - 110) * 0.1) # Up to +10 points

        # If we have simulation results, we can refine risk estimates
        if simulation_results and strategy_key in ['REDUCE_LOAD', 'SCHEDULE_MAINTENANCE']:
            # This would compare simulated outcomes - simplified for now
            pass

        return adjustment

    def _generate_explanation(self, optimal_strategy: str,
                          intervention_evaluations: Dict[str, Any],
                          telemetry_data: Dict[str, Any] = None,
                          health_metrics: Dict[str, Any] = None,
                          rul_metrics: Dict[str, Any] = None,
                          risk_assessment: Dict[str, Any] = None,
                          simulation_results: Dict[str, Any] = None) -> List[str]:
        """Generate human-readable explanation for the recommendation"""
        explanation = []

        optimal_info = self.intervention_strategies[optimal_strategy]
        optimal_eval = intervention_evaluations[optimal_strategy]

        # Start with the recommendation
        explanation.append(f"RECOMMENDATION: {optimal_info['name']}")

        # Add key factors driving the decision
        explanation.append(f"Decision Score: {optimal_eval['total_score']:.1f}/100 (lower is better)")

        # Show the breakdown of why this option was selected
        breakdown = optimal_eval['breakdown']
        explanation.append("KEY FACTORS:")
        explanation.append(f"  • Risk: {breakdown['risk']['raw_score']:.1f}/100 "
                          f"(weight: {breakdown['risk']['weight']*100:.0f}%)")
        explanation.append(f"  • Cost: ${breakdown['cost']['raw_value']:,} "
                          f"(score: {breakdown['cost']['raw_score']:.1f}/100, "
                          f"weight: {breakdown['cost']['weight']*100:.0f}%)")
        explanation.append(f"  • Downtime: {breakdown['downtime']['raw_value']} hours "
                          f"(score: {breakdown['downtime']['raw_score']:.1f}/100, "
                          f"weight: {breakdown['downtime']['weight']*100:.0f}%)")
        explanation.append(f"  • Life Impact: {breakdown['life_impact']['raw_value']}x "
                          f"(score: {breakdown['life_impact']['raw_score']:.1f}/100, "
                          f"weight: {breakdown['life_impact']['weight']*100:.0f}%)")

        # Add context from current asset condition
        explanation.append("\nCURRENT ASSET CONDITION:")
        if health_metrics:
            explanation.append(f"  • Health Score: {health_metrics.get('health_score', 'N/A')}/100")
            explanation.append(f"  • Failure Probability: {health_metrics.get('failure_probability', 0)*100:.1f}%")
            explanation.append(f"  • Risk Level: {health_metrics.get('risk_level', 'N/A')}")
        if rul_metrics:
            explanation.append(f"  • Remaining Life: {rul_metrics.get('rul_years', 'N/A'):.1f} years")
            explanation.append(f"  • Life Used: {rul_metrics.get('percent_life_used', 'N/A'):.1f}%")
        if telemetry_data:
            explanation.append(f"  • Load: {telemetry_data.get('load_percent', 'N/A')}%")
            explanation.append(f"  • Winding Temp: {telemetry_data.get('winding_temp_c', 'N/A')}°C")
            explanation.append(f"  • Oil Temp: {telemetry_data.get('oil_temp_c', 'N/A')}°C")

        # Add simulation insights if available
        if simulation_results:
            explanation.append("\nSIMULATION INSIGHTS:")
            explanation.append(f"  • Simulation shows potential outcomes for different scenarios")
            if optimal_strategy == 'REDUCE_LOAD':
                explanation.append("  • Load reduction simulated to decrease temperature and extend life")
            elif optimal_strategy == 'SCHEDULE_MAINTENANCE':
                explanation.append("  • Maintenance simulated to address degradation factors")
            elif optimal_strategy == 'REPLACE_ASSET':
                explanation.append("  • Replacement provides baseline performance with zero degradation risk")

        # Compare with alternatives
        explanation.append("\nALTERNATIVE CONSIDERATIONS:")
        sorted_interventions = sorted(
            intervention_evaluations.items(),
            key=lambda x: x[1]['total_score']
        )

        for strategy_key, eval_data in sorted_interventions:
            if strategy_key == optimal_strategy:
                explanation.append(f"  • {eval_data['strategy_name']}: SELECTED (score: {eval_data['total_score']:.1f})")
            else:
                explanation.append(f"  • {eval_data['strategy_name']}: {eval_data['total_score']:.1f}/100")

        # Add specific reasoning based on the chosen strategy
        explanation.append(f"\nWHY THIS OPTION WAS SELECTED:")
        if optimal_strategy == 'CONTINUE_OPERATION':
            explanation.append("  • Current operating conditions are within acceptable limits")
            explanation.append("  • Intervention costs and risks outweigh benefits")
            explanation.append("  • Continue with enhanced monitoring rather than immediate action")
        elif optimal_strategy == 'REDUCE_LOAD':
            explanation.append("  • Load reduction provides significant risk reduction with minimal cost")
            explanation.append("  • Avoids service interruption while addressing thermal stress")
            explanation.append("  • Particularly effective when overload or high temperature is present")
        elif optimal_strategy == 'SCHEDULE_MAINTENANCE':
            explanation.append("  • Maintenance addresses root causes of degradation")
            explanation.append("  • Provides good balance of cost, downtime, and life extension")
            explanation.append("  • Recommended when condition warrants intervention but not emergency action")
        elif optimal_strategy == 'REPLACE_ASSET':
            explanation.append("  • Current condition justifies replacement investment")
            explanation.append("  • Eliminates ongoing risk and provides full life extension")
            explanation.append("  • Selected when repair/maintenance would be uneconomical or ineffective")

        # Add what happens if we do nothing
        explanation.append(f"\nWHAT IF WE DO NOTHING:")
        continue_eval = intervention_evaluations.get('CONTINUE_OPERATION')
        if continue_eval:
            explanation.append(f"  • Continuing operation would result in score: {continue_eval['total_score']:.1f}/100")
            if continue_eval['total_score'] > optimal_eval['total_score'] + 10:
                explanation.append("  • Significantly higher risk and lower life expectancy vs recommended action")
            else:
                explanation.append("  • Similar outcome to recommendation but less optimal resource allocation")

        return explanation

    def _get_default_recommendation(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a safe default recommendation when optimization fails"""
        logger.warning("Returning default recommendation due to optimization error")

        # Simple rule-based fallback
        load_percent = telemetry_data.get('load_percent', 0.0)
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)

        if load_percent > 115 or winding_temp > 110:
            recommended = 'REPLACE_ASSET'
        elif load_percent > 105 or winding_temp > 100:
            recommended = 'SCHEDULE_MAINTENANCE'
        elif load_percent > 90 or winding_temp > 90:
            recommended = 'REDUCE_LOAD'
        else:
            recommended = 'CONTINUE_OPERATION'

        return {
            'asset_id': telemetry_data.get('asset_id', 'T-01'),
            'recommended_intervention': self.intervention_strategies[recommended]['name'],
            'recommended_intervention_key': recommended,
            'intervention_scores': {
                key: {
                    'name': info['name'],
                    'total_score': 50.0,  # Neutral score
                    'risk_score': 50.0,
                    'cost_score': 50.0,
                    'downtime_score': 50.0,
                    'life_impact_score': 50.0,
                    'breakdown': {}
                }
                for key, info in self.intervention_strategies.items()
            },
            'optimal_intervention_score': 50.0,
            'explanation': [
                f"RECOMMENDATION: {self.intervention_strategies[recommended]['name']}",
                "Decision Score: 50.0/100 (fallback recommendation)",
                "KEY FACTORS: Using rule-based fallback due to system error",
                f"  • Load: {load_percent}%",
                f"  • Winding Temp: {winding_temp}°C",
                "WHY THIS OPTION WAS SELECTED:",
                "  • Rule-based fallback logic applied",
                "WHAT IF WE DO NOTHING:",
                "  • System error prevented full optimization"
            ],
            'assessment_details': {
                'timestamp': pd.Timestamp.now().isoformat(),
                'error': 'Optimization failed - using fallback'
            }
        }


# Factory function for easy instantiation
def create_decision_optimizer() -> TransformerDecisionOptimizer:
    """
    Create and return a transformer decision optimizer instance

    Returns:
        TransformerDecisionOptimizer instance
    """
    return TransformerDecisionOptimizer()


# Example usage and testing
if __name__ == "__main__":
    print("Transformer Decision Optimizer - Testing")
    print("=" * 50)

    # Create decision optimizer
    optimizer = create_decision_optimizer()

    # Test cases representing different scenarios
    test_scenarios = [
        {
            'name': 'Normal Operation - Healthy Transformer',
            'asset_id': 'T-01',
            'load_percent': 60,
            'voltage_kv': 23.0,
            'current_a': 150,
            'ambient_temp_c': 25,
            'oil_temp_c': 40,
            'winding_temp_c': 55,
            'vibration_mm_s': 1.0,
            'operating_hours': 8760 * 2  # 2 years
        },
        {
            'name': 'Elevated Load - Moderate Stress',
            'asset_id': 'T-01',
            'load_percent': 85,
            'voltage_kv': 22.8,
            'current_a': 212,
            'ambient_temp_c': 30,
            'oil_temp_c': 50,
            'winding_temp_c': 75,
            'vibration_mm_s': 1.2,
            'operating_hours': 8760 * 5  # 5 years
        },
        {
            'name': 'Thermal Stress - High Temperature',
            'asset_id': 'T-01',
            'load_percent': 75,
            'voltage_kv': 23.0,
            'current_a': 188,
            'ambient_temp_c': 35,
            'oil_temp_c': 65,
            'winding_temp_c': 95,
            'vibration_mm_s': 1.8,
            'operating_hours': 8760 * 8  # 8 years
        },
        {
            'name': 'Overload Condition',
            'asset_id': 'T-01',
            'load_percent': 110,
            'voltage_kv': 22.5,
            'current_a': 275,
            'ambient_temp_c': 32,
            'oil_temp_c': 70,
            'winding_temp_c': 100,
            'vibration_mm_s': 2.0,
            'operating_hours': 8760 * 3  # 3 years
        },
        {
            'name': 'Aged Transformer - Poor Condition',
            'asset_id': 'T-01',
            'load_percent': 50,
            'voltage_kv': 22.0,
            'current_a': 125,
            'ambient_temp_c': 28,
            'oil_temp_c': 80,
            'winding_temp_c': 105,
            'vibration_mm_s': 2.5,
            'operating_hours': 8760 * 15  # 15 years - aged unit
        }
    ]

    # Create supporting models for comprehensive assessment
    from .health_model import create_health_model
    from .rul_model import create_rul_model
    from .risk_model import create_risk_model
    health_model = create_health_model()
    rul_model = create_rul_model()
    risk_model = create_risk_model()

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 40)

        # Get supporting assessments
        health_metrics = health_model.predict_health(scenario)
        rul_metrics = rul_model.predict_rul(scenario, health_metrics)
        risk_assessment = risk_model.assess_comprehensive_risk(scenario, health_metrics, rul_metrics)

        # Simulate digital twin results for what-if analysis
        simulation_results = {
            'scenario_simulations': {
                'REDUCE_LOAD': {
                    'winding_temp_c': scenario['winding_temp_c'] - 10,
                    'health_score': min(100, health_metrics['health_score'] + 15),
                    'rul_years': rul_metrics['rul_years'] * 1.3
                },
                'SCHEDULE_MAINTENANCE': {
                    'winding_temp_c': scenario['winding_temp_c'] - 5,
                    'health_score': min(100, health_metrics['health_score'] + 10),
                    'rul_years': rul_metrics['rul_years'] * 1.5
                }
            }
        }

        # Run decision optimization
        result = optimizer.evaluate_interventions(
            scenario, health_metrics, rul_metrics, risk_assessment, simulation_results
        )

        print(f"🎯 RECOMMENDATION: {result['recommended_intervention']}")
        print(f"📊 SCORE: {result['optimal_intervention_score']}/100")
        print(f"📋 EXPLANATION:")
        for line in result['explanation'][:8]:  # Show first 8 lines
            print(f"   {line}")

        print(f"\n📈 INTERVENTION SCORES:")
        for key, eval_data in result['intervention_scores'].items():
            name = eval_data['name']
            score = eval_data['total_score']
            marker = " >>>" if key == result['recommended_intervention_key'] else ""
            print(f"   {name}: {score}/100{marker}")
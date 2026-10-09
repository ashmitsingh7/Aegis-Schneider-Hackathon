/**
 * Advanced Analytics Service for Aegis Platform
 * Provides root cause analysis, what-if scenario planning, and optimization capabilities
 */

import { apiService } from '@/lib/apiService';
import type {
  HealthResponse,
  RULResponse,
  RiskResponse,
  DecisionResponse,
  SimulationResponse,
  TelemetryData
} from '@/types/api';

// Advanced Analytics Interfaces
interface RootCauseAnalysis {
  primaryCause: string;
  contributingFactors: Array<{ factor: string; impact: number; confidence: number }>;
  recommendedActions: Array<{ action: string; priority: 'high' | 'medium' | 'low'; expectedImpact: number }>;
  timeline: { immediate: string; shortTerm: string; longTerm: string };
}

interface WhatIfScenario {
  scenarioName: string;
  description: string;
  parameters: Record<string, number | boolean>;
  predictedOutcome: {
    healthScoreChange: number;
    riskLevelChange: string;
    rulChangeDays: number;
    costImpact: number;
  };
  confidence: number;
}

interface OptimizationResult {
  recommendedAction: string;
  confidenceScore: number;
  expectedBenefits: Array<{ benefit: string; value: string | number }>;
  implementation: {
    timeline: string;
    resources: string[];
    prerequisites: string[];
  };
  roiAnalysis: {
    initialCost: number;
    annualSavings: number;
    paybackPeriodMonths: number;
  };
}

class AdvancedAnalyticsService {
  /**
   * Perform root cause analysis on asset issues
   */
  async performRootCauseAnalysis(
    assetId: string,
    telemetry: TelemetryData
  ): Promise<RootCauseAnalysis> {
    try {
      // Get comprehensive assessment data
      const [healthResult, riskResult] = await Promise.all([
        apiService.getAssetHealth(assetId, telemetry),
        apiService.getAssetRisk(assetId, telemetry)
      ]);

      // Analyze contributing factors
      const contributingFactors = this.analyzeContributingFactors(healthResult, riskResult);

      // Determine primary cause
      const primaryCause = this.determinePrimaryCause(contributingFactors);

      // Generate recommended actions
      const recommendedActions = this.generateRecommendedActions(primaryCause, contributingFactors);

      // Create timeline
      const timeline = this.createRemediationTimeline(primaryCause, recommendedActions);

      return {
        primaryCause,
        contributingFactors,
        recommendedActions,
        timeline
      };
    } catch (error) {
      console.error('Error performing root cause analysis:', error);
      // Return fallback analysis
      return this.getFallbackRootCauseAnalysis();
    }
  }

  /**
   * Run what-if scenario analysis for different intervention strategies
   */
  async runWhatIfScenarios(
    assetId: string,
    baseTelemetry: TelemetryData,
    scenarios: Array<{
      name: string;
      description: string;
      modifications: Partial<TelemetryData>;
    }>
  ): Promise<WhatIfScenario[]> {
    try {
      const results: WhatIfScenario[] = [];

      for (const scenario of scenarios) {
        // Modify telemetry based on scenario
        const modifiedTelemetry = { ...baseTelemetry, ...scenario.modifications };

        // Get predictions for modified scenario
        const [healthResult, riskResult] = await Promise.all([
          apiService.getAssetHealth(assetId, modifiedTelemetry),
          apiService.getAssetRisk(assetId, modifiedTelemetry)
        ]);

        // Get baseline for comparison
        const [baselineHealth, baselineRisk] = await Promise.all([
          apiService.getAssetHealth(assetId, baseTelemetry),
          apiService.getAssetRisk(assetId, baseTelemetry)
        ]);

        // Calculate predicted outcomes
        const healthScoreChange = Math.round(healthResult.health_score - baselineHealth.health_score);
        const riskLevelChange = this.calculateRiskLevelChange(
          baselineRisk.overall_risk_level,
          riskResult.overall_risk_level
        );
        const rulChangeDays = Math.round(
          (riskResult.assessment_details?.remaining_life_days || 0) -
          (baselineRisk.assessment_details?.remaining_life_days || 0)
        );
        const costImpact = this.estimateCostImpact(scenario.name, healthScoreChange, riskLevelChange);

        results.push({
          scenarioName: scenario.name,
          description: scenario.description,
          parameters: scenario.modifications,
          predictedOutcome: {
            healthScoreChange,
            riskLevelChange,
            rulChangeDays,
            costImpact
          },
          confidence: this.calculateScenarioConfidence(healthResult, riskResult)
        });
      }

      // Sort by predicted improvement (best first)
      return results.sort((a, b) =>
        b.predictedOutcome.healthScoreChange - a.predictedOutcome.healthScoreChange
      );
    } catch (error) {
      console.error('Error running what-if scenarios:', error);
      return this.getFallbackWhatIfScenarios();
    }
  }

  /**
   * Optimize maintenance/intervention strategy
   */
  async optimizeMaintenanceStrategy(
    assetId: string,
    telemetry: TelemetryData,
    constraints: {
      budget?: number;
      maxDowntimeHours?: number;
      riskThreshold?: string;
    } = {}
  ): Promise<OptimizationResult> {
    try {
      // Get current state assessment
      const [healthResult, riskResult, decisionResult] = await Promise.all([
        apiService.getAssetHealth(assetId, telemetry),
        apiService.getAssetRisk(assetId, telemetry),
        apiService.getAssetDecision(assetId, telemetry)
      ]);

      // Analyze all intervention options
      const interventionOptions = this.analyzeInterventionOptions(
        decisionResult,
        healthResult,
        riskResult,
        constraints
      );

      // Select optimal strategy
      const optimalStrategy = this.selectOptimalStrategy(interventionOptions, constraints);

      // Calculate ROI analysis
      const roiAnalysis = this.calculateROI(optimalStrategy, healthResult, riskResult);

      return {
        recommendedAction: optimalStrategy.action,
        confidenceScore: optimalStrategy.confidence,
        expectedBenefits: optimalStrategy.benefits,
        implementation: optimalStrategy.implementation,
        roiAnalysis
      };
    } catch (error) {
      console.error('Error optimizing maintenance strategy:', error);
      return this.getFallbackOptimizationResult();
    }
  }

  // Private helper methods

  private analyzeContributingFactors(
    healthResult: HealthResponse,
    riskResult: RiskResponse
  ): Array<{ factor: string; impact: number; confidence: number }> {
    const factors: Array<{ factor: string; impact: number; confidence: number }> = [];

    // Analyze health indicators
    if (healthResult.health_score < 60) {
      factors.push({
        factor: 'Poor Health Score',
        impact: (100 - healthResult.health_score) / 100,
        confidence: healthResult.confidence
      });
    }

    if (healthResult.failure_probability > 0.3) {
      factors.push({
        factor: 'High Failure Probability',
        impact: healthResult.failure_probability,
        confidence: healthResult.confidence
      });
    }

    // Analyze risk factors
    Object.entries(riskResult.risk_scores).forEach(([factor, score]) => {
      if (score > 0.4) { // Significant risk threshold
        factors.push({
          factor: this.formatRiskFactorName(factor),
          impact: score,
          confidence: riskResult.confidence
        });
      }
    });

    // Sort by impact descending
    return factors.sort((a, b) => b.impact - a.impact);
  }

  private determinePrimaryCause(
    factors: Array<{ factor: string; impact: number; confidence: number }>
  ): string {
    if (factors.length === 0) return 'Normal wear and tear';
    return factors[0].factor;
  }

  private generateRecommendedActions(
    primaryCause: string,
    factors: Array<{ factor: string; impact: number; confidence: number }>
  ): Array<{ action: string; priority: 'high' | 'medium' | 'low'; expectedImpact: number }> {
    const actions: Array<{ action: string; priority: 'high' | 'medium' | 'low'; expectedImpact: number }> = [];

    // Map causes to actions
    const causeActionMap: Record<string, Array<{ action: string; priority: 'high' | 'medium' | 'low'; impact: number }>> = {
      'Poor Health Score': [
        { action: 'Schedule comprehensive diagnostic testing', priority: 'high', impact: 25 },
        { action: 'Review maintenance history and procedures', priority: 'medium', impact: 15 },
        { action: 'Consider load reduction measures', priority: 'medium', impact: 20 }
      ],
      'High Failure Probability': [
        { action: 'Implement increased monitoring schedule', priority: 'high', impact: 30 },
        { action: 'Prepare emergency response plan', priority: 'high', impact: 25 },
        { action: 'Evaluate redundancy options', priority: 'medium', impact: 20 }
      ],
      'Thermal Risk': [
        { action: 'Reduce electrical loading immediately', priority: 'high', impact: 35 },
        { action: 'Check cooling system effectiveness', priority: 'high', impact: 25 },
        { action: 'Inspect for blocked ventilation paths', priority: 'medium', impact: 15 }
      ],
      'Electrical Risk': [
        { action: 'Verify proper grounding and connections', priority: 'high', impact: 30 },
        { action: 'Check for overvoltage or harmonics', priority: 'medium', impact: 20 },
        { action: 'Review load balancing across phases', priority: 'medium', impact: 20 }
      ],
      'Insulation Risk': [
        { action: 'Schedule dielectric testing', priority: 'high', impact: 30 },
        { action: 'Check for moisture ingress', priority: 'medium', impact: 20 },
        { action: 'Review temperature cycling history', priority: 'medium', impact: 20 }
      ]
    };

    // Get actions for primary cause
    const primaryActions = causeActionMap[primaryCause] ||
      [{ action: 'Continue monitoring and scheduled maintenance', priority: 'medium', impact: 10 }];

    // Convert to expected format
    primaryActions.forEach(action => {
      actions.push({
        action: action.action,
        priority: action.priority,
        expectedImpact: action.impact
      });
    });

    // Limit to top 3 actions
    return actions.slice(0, 3);
  }

  private createRemediationTimeline(
    primaryCause: string,
    actions: Array<{ action: string; priority: 'high' | 'medium' | 'low'; expectedImpact: number }>
  ): { immediate: string; shortTerm: string; longTerm: string } {
    const hasHighPriority = actions.some(action => action.priority === 'high');

    return {
      immediate: hasHighPriority ? 'Within 24 hours' : 'Within 1 week',
      shortTerm: 'Within 1-4 weeks',
      longTerm: 'Within 1-3 months'
    };
  }

  private calculateRiskLevelChange(baseline: string, modified: string): string {
    const riskLevels: Record<string, number> = {
      'LOW': 1,
      'MEDIUM': 2,
      'HIGH': 3,
      'CRITICAL': 4
    };

    const baselineNum = riskLevels[baseline] || 2;
    const modifiedNum = riskLevels[modified] || 2;
    const change = modifiedNum - baselineNum;

    if (change > 0) return `+${change} level(s)`;
    if (change < 0) return `${change} level(s)`;
    return 'No change';
  }

  private estimateCostImpact(
    scenarioName: string,
    healthScoreChange: number,
    riskLevelChange: string
  ): number {
    // Simplified cost impact estimation
    let baseCost = 0;

    // Cost associated with health score changes
    if (healthScoreChange < 0) {
      baseCost += Math.abs(healthScoreChange) * 100; // $100 per point health decrease
    } else {
      baseCost -= healthScoreChange * 50; // Savings for health improvement
    }

    // Cost associated with risk level changes
    const riskCostMap: Record<string, number> = {
      '+1 level(s)': 5000,
      '+2 level(s)': 15000,
      '+3 level(s)': 30000,
      '-1 level(s)': -2000,
      '-2 level(s)': -5000,
      '-3 level(s)': -10000,
      'No change': 0
    };

    baseCost += riskCostMap[riskLevelChange] || 0;

    // Scenario-specific adjustments
    switch (scenarioName.toLowerCase()) {
      case 'continue operation':
        baseCost += 0;
        break;
      case 'reduce load':
        baseCost += 5000; // Operational adjustment cost
        break;
      case 'schedule maintenance':
        baseCost += 15000; // Maintenance cost
        break;
      case 'replace asset':
        baseCost += 200000; // Replacement cost
        break;
      default:
        baseCost += 1000; // Default small cost
    }

    return Math.max(0, baseCost);
  }

  private calculateScenarioConfidence(
    healthResult: HealthResponse,
    riskResult: RiskResponse
  ): number {
    // Average of health and risk confidence scores
    return Math.round((healthResult.confidence + riskResult.confidence) / 2 * 100) / 100;
  }

  private analyzeInterventionOptions(
    decisionResult: DecisionResponse,
    healthResult: HealthResponse,
    riskResult: RiskResponse,
    constraints: {
      budget?: number;
      maxDowntimeHours?: number;
      riskThreshold?: string;
    }
  ): Array<{
    action: string;
    confidence: number;
    benefits: Array<{ benefit: string; value: string | number }>;
    implementation: {
      timeline: string;
      resources: string[];
      prerequisites: string[];
    };
  }> {
    // This would normally come from the decision engine, but we'll simulate based on available data
    const interventions = [
      {
        action: 'Continue Operation',
        confidence: 0.7,
        benefits: [
          { benefit: 'No immediate cost', value: '$0' },
          { benefit: 'Maintains service continuity', value: '100%' },
          { benefit: 'Zero downtime', value: '0 hours' }
        ],
        implementation: {
          timeline: 'Ongoing',
          resources: ['Existing staff'],
          prerequisites: ['None']
        }
      },
      {
        action: 'Reduce Load',
        confidence: 0.85,
        benefits: [
          { benefit: 'Reduced thermal stress', value: '25-40%' },
          { benefit: 'Lower failure risk', value: '30-50% reduction' },
          { benefit: 'Minimal cost', value: '$5,000-$10,000' }
        ],
        implementation: {
          timeline: 'Immediate to 1 week',
          resources: ['Operations team', 'SCADA system'],
          prerequisites: ['Load capacity analysis']
        }
      },
      {
        action: 'Schedule Maintenance',
        confidence: 0.75,
        benefits: [
          { benefit: 'Addresses root causes', value: '60-80% effectiveness' },
          { benefit: 'Planned approach', value: 'Controlled execution' },
          { benefit: 'Extended asset life', value: '6-18 months additional' }
        ],
        implementation: {
          timeline: '2-8 weeks planning + execution',
          resources: ['Maintenance crew', 'Specialized equipment', 'Outage coordination'],
          prerequisites: ['Outage approval', 'Parts availability', 'Weather window']
        }
      },
      {
        action: 'Replace Asset',
        confidence: 0.6,
        benefits: [
          { benefit: 'Like-new condition', value: '100%' },
          { benefit: 'Zero existing issues', value: 'Complete renewal' },
          { benefit: 'Latest technology', value: 'Modern efficiency standards' }
        ],
        implementation: {
          timeline: '3-6 months',
          resources: ['Project team', 'Contractors', 'Engineering review'],
          prerequisites: ['Budget approval', 'Procurement cycle', 'Installation planning']
        }
      }
    ];

    // Apply constraint filtering
    return interventions.filter(intervention => {
      // Budget constraint
      if (constraints.budget !== undefined) {
        const cost = this.extractCostFromValue(intervention.benefits.find(b => b.benefit.includes('cost'))?.value || '$0');
        if (cost > constraints.budget) return false;
      }

      // Downtime constraint (simplified)
      if (constraints.maxDowntimeHours !== undefined) {
        const downtime = this.extractDowntimeFromValue(intervention.benefits.find(b => b.benefit.includes('downtime'))?.value || '0');
        if (downtime > constraints.maxDowntimeHours) return false;
      }

      return true;
    });
  }

  private selectOptimalStrategy(
    options: Array<{
      action: string;
      confidence: number;
      benefits: Array<{ benefit: string; value: string | number }>;
      implementation: {
        timeline: string;
        resources: string[];
        prerequisites: string[];
      };
    }>,
    constraints: {
      budget?: number;
      maxDowntimeHours?: number;
      riskThreshold?: string;
    }
  ): {
    action: string;
    confidence: number;
    benefits: Array<{ benefit: string; value: string | number }>;
    implementation: {
      timeline: string;
      resources: string[];
      prerequisites: string[];
    };
  } {
    if (options.length === 0) {
      return options[0]; // Fallback to first option
    }

    // Simple scoring: confidence * benefit score
    const scoredOptions = options.map(option => {
      const benefitScore = this.calculateBenefitScore(option.benefits);
      return {
        ...option,
        score: option.confidence * benefitScore
      };
    });

    // Return highest scoring option
    return scoredOptions.reduce((best, current) =>
      current.score > best.score ? current : best
    );
  }

  private calculateBenefitScore(benefits: Array<{ benefit: string; value: string | number }>): number {
    // Simple heuristic: more benefits and positive indicators = higher score
    let score = benefits.length * 0.2; // Base score per benefit

    benefits.forEach(benefit => {
      const valueStr = benefit.value.toString().toLowerCase();

      // Positive indicators
      if (valueStr.includes('%') && !valueStr.includes('-')) {
        const num = parseFloat(valueStr);
        if (!isNaN(num) && num > 0) score += Math.min(num / 10, 1); // Up to 1 point for percentages
      }

      if (valueStr.includes('+') || valueStr.includes('increase') || valueStr.includes('improve')) {
        score += 0.5;
      }

      if (valueStr.includes('reduction') || valueStr.includes('decrease') || valueStr.includes('lower')) {
        score += 0.5;
      }

      // Negative indicators
      if (valueStr.includes('high cost') || valueStr.includes('expensive')) {
        score -= 0.3;
      }

      if (valueStr.includes('downtime') && !valueStr.includes('zero') && !valueStr.includes('0')) {
        score -= 0.2;
      }
    });

    return Math.max(0.1, Math.min(1.0, score)); // Clamp between 0.1 and 1.0
  }

  private calculateROI(
    strategy: {
      action: string;
      confidence: number;
      benefits: Array<{ benefit: string; value: string | number }>;
      implementation: {
        timeline: string;
        resources: string[];
        prerequisites: string[];
      };
    },
    healthResult: HealthResponse,
    riskResult: RiskResponse
  ): {
    initialCost: number;
    annualSavings: number;
    paybackPeriodMonths: number;
  } {
    // Extract cost from strategy benefits
    const costBenefit = strategy.benefits.find(b =>
      b.benefit.toLowerCase().includes('cost') ||
      b.benefit.toLowerCase().includes('expense')
    );

    let initialCost = 5000; // Default
    if (costBenefit) {
      initialCost = this.extractCostFromValue(costBenefit.value);
    }

    // Estimate annual savings based on risk reduction and life extension
    let annualSavings = 0;

    // Savings from avoided failures
    const failureProbability = healthResult.failure_probability;
    const avoidedFailureValue = failureProbability * 100000; // $100k per avoided failure
    annualSavings += avoidedFailureValue * strategy.confidence * 0.3; // 30% effectiveness

    // Savings from extended life
    const lifeExtensionBenefit = strategy.benefits.find(b =>
      b.benefit.toLowerCase().includes('life') &&
      (b.benefit.toLowerCase().includes('extend') || b.benefit.toLowerCase().includes('additional'))
    );

    if (lifeExtensionBenefit) {
      const lifeValue = this.extractLifeValue(lifeExtensionBenefit.value);
      annualSavings += lifeValue * 0.1; // 10% of life extension value per year
    }

    // Calculate payback period
    const paybackPeriodMonths = annualSavings > 0 ?
      (initialCost / annualSavings) * 12 :
      999; // Effectively infinite if no savings

    return {
      initialCost,
      annualSavings: Math.max(0, annualSavings),
      paybackPeriodMonths: Math.min(999, paybackPeriodMonths)
    };
  }

  private extractCostFromValue(value: string): number {
    const numStr = value.toString().replace(/[^\d.-]/g, '');
    const num = parseFloat(numStr);
    return isNaN(num) ? 0 : num;
  }

  private extractDowntimeFromValue(value: string): number {
    const numStr = value.toString().replace(/[^\d.-]/g, '');
    const num = parseFloat(numStr);
    return isNaN(num) ? 0 : num;
  }

  private extractLifeValue(value: string): number {
    const numStr = value.toString().replace(/[^\d.-]/g, '');
    const num = parseFloat(numStr);
    return isNaN(num) ? 0 : num;
  }

  private formatRiskFactorName(factor: string): string {
    return factor
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  // Fallback methods for error cases

  private getFallbackRootCauseAnalysis(): RootCauseAnalysis {
    return {
      primaryCause: 'Insufficient data for analysis',
      contributingFactors: [
        { factor: 'Data Collection Issues', impact: 0.5, confidence: 0.7 },
        { factor: 'System Limitations', impact: 0.3, confidence: 0.8 }
      ],
      recommendedActions: [
        {
          action: 'Improve data quality and collection frequency',
          priority: 'high',
          expectedImpact: 40
        },
        {
          action: 'Perform manual inspection and testing',
          priority: 'medium',
          expectedImpact: 30
        }
      ],
      timeline: {
        immediate: 'Within 24 hours',
        shortTerm: 'Within 1 week',
        longTerm: 'Within 1 month'
      }
    };
  }

  private getFallbackWhatIfScenarios(): WhatIfScenario[] {
    return [
      {
        scenarioName: 'Continue Operation',
        description: 'Maintain current operating parameters',
        parameters: { load_percent: 75, ambient_temp_c: 30 },
        predictedOutcome: {
          healthScoreChange: 0,
          riskLevelChange: 'No change',
          rulChangeDays: 0,
          costImpact: 0
        },
        confidence: 0.8
      },
      {
        scenarioName: 'Reduce Load by 15%',
        description: 'Decrease electrical loading to reduce thermal stress',
        parameters: { load_percent: 63, ambient_temp_c: 30 },
        predictedOutcome: {
          healthScoreChange: 5,
          riskLevelChange: '-1 level(s)',
          rulChangeDays: 30,
          costImpact: 2000
        },
        confidence: 0.75
      }
    ];
  }

  private getFallbackOptimizationResult(): OptimizationResult {
    return {
      recommendedAction: 'Continue Operation with Monitoring',
      confidenceScore: 0.7,
      expectedBenefits: [
        { benefit: 'No immediate expenditure', value: '$0' },
        { benefit: 'Maintains service availability', value: '100%' },
        { benefit: 'Allows time for further analysis', value: 'Flexible timeline' }
      ],
      implementation: {
        timeline: 'Ongoing monitoring',
        resources: ['Existing personnel'],
        prerequisites: ['None']
      },
      roiAnalysis: {
        initialCost: 0,
        annualSavings: 0,
        paybackPeriodMonths: 0
      }
    };
  }
}

// Export a singleton instance
export const advancedAnalyticsService = new AdvancedAnalyticsService();

// Export types
export type {
  RootCauseAnalysis,
  WhatIfScenario,
  OptimizationResult
};
# Using Aegis Advanced Features

This guide demonstrates how to use the advanced visualization and analytics features recently added to the Aegis platform.

## Accessing the Advanced Features

The advanced features are accessible through the main navigation menu:

1. Start the Aegis platform (backend and frontend)
2. Navigate to http://localhost:3000 in your browser
3. Use the top navigation bar to access different sections
4. The new "Analytics" link appears alongside Dashboard, Demo, Decision, and Simulation

## Feature Demonstration

### 1. Advanced Visualization Dashboard

The main dashboard now includes enhanced visual components:

#### Health Gauge
- **Location**: Top-left section of the dashboard
- **What it shows**: Circular gauge displaying asset health score (0-100)
- **Color coding**: 
  - Red (<40): Poor health requiring immediate attention
  - Amber (40-60): Fair health needing monitoring
  - Green (>60): Good health status
- **Interaction**: Hover to see exact score and health status description

#### Telemetry Trends Chart
- **Location**: Middle section of the dashboard
- **What it shows**: 24-hour trends of key operational parameters
- **Tracks**:
  - Electrical Load (% of rated capacity)
  - Oil Temperature (°C)
  - Winding Temperature (°C) 
  - Vibration Levels (mm/s)
- **Interaction**: Hover over lines to see exact values at specific times
- **Patterns to watch for**:
  - Correlated increases in load and temperature
  - Vibration spikes indicating mechanical issues
  - Temperature lag behind load changes (thermal inertia)

#### Risk Factors Breakdown
- **Location**: Bottom-right section of the dashboard
- **What it shows**: Pie chart displaying contribution of different risk types
- **Risk Categories**:
  - Thermal: Heat-related stresses
  - Electrical: Voltage, current, and loading stresses
  - Insulation: Dielectric strength and aging
  - Mechanical: Vibration and physical stresses
  - Aging: Cumulative wear and time-based degradation
- **Interaction**: Hover over slices to see exact percentage values

#### RUL Indicator
- **Location**: Bottom section of the dashboard  
- **What it shows**: Circular progress bar showing Remaining Useful Life
- **Calculation**: Based on asset condition, loading, and environmental factors
- **Color coding**: Same as health gauge (red/amber/green)
- **Center display**: Exact percentage of life remaining

### 2. Advanced Analytics Center

Navigate to the Analytics page (/analytics) to access the sophisticated analytical capabilities:

#### Root Cause Analysis Panel
- **Purpose**: Diagnose the underlying reasons for asset issues
- **Key Sections**:
  - **Primary Cause**: The single most significant factor contributing to issues
  - **Contributing Factors**: Secondary factors with impact percentages and confidence levels
  - **Recommended Actions**: Prioritized steps to address the identified causes
  - **Remediation Timeline**: Suggested timing for different types of actions

- **How to Use**:
  1. Review the primary cause to understand the main issue
  2. Examine contributing factors to see what's making it worse
  3. Follow recommended actions in priority order
  4. Use the timeline to plan when to execute different actions

#### What-If Scenario Planner
- **Purpose**: Compare different intervention strategies before implementing them
- **How to Use**:
  1. Review each scenario card showing a different approach
  2. Check the "RECOMMENDED" badge for the AI's top choice
  3. Compare outcome predictions:
     - Health Score Change: Improvement (+) or decline (-) in points
     - RUL Change: Additional (+) or lost (-) days of life
     - Cost Impact: Money saved (-) or spent (+)
  4. Examine the parameters modified for each scenario
  5. Note the confidence score indicating prediction reliability

- **Common Scenarios Included**:
  - **Continue Operation**: Baseline - no changes
  - **Reduce Load by 10%/25%**: Load reduction for thermal relief
  - **Improve Cooling**: Lower ambient temperature through better cooling
  - **Reduce Vibration**: Mechanical stabilization efforts
  - *(Additional scenarios can be added based on specific asset types)*

#### Maintenance Optimization Recommendations
- **Purpose**: Find the best action given real-world constraints
- **Key Sections**:
  - **Recommended Strategy**: The optimal action given your constraints
  - **Expected Benefits**: What you'll gain from implementing this strategy
  - **Implementation Plan**: How to execute the recommendation
  - **Return on Investment**: Financial justification for the action

- **How to Use**:
  1. Check the constraints shown (budget, downtime limits, risk thresholds)
  2. Review the recommended strategy and its confidence level
  3. Examine expected benefits to understand the value proposition
  4. Read the implementation plan for execution details
  5. Review ROI to understand the financial justification
  6. Note payback period - how quickly the investment returns value

- **Typical Constraints to Consider**:
  - **Budget**: Available funds for the intervention
  - **Max Downtime**: Maximum allowable outage time
  - **Risk Threshold**: Maximum acceptable risk level after intervention

### 3. Practical Example Workflow

Here's how an engineer might use these features in practice:

**Situation**: Received an alert about elevated winding temperature on Transformer T-01

**Step 1: Initial Assessment** (Dashboard)
- Check Health Gauge: Shows 62/100 (Amber - Fair)
- Notice Telemetry Trends: Winding temp rising over past 4 hours
- See Risk Factors: Thermal risk at 45% (highest contributor)
- Note RUL Indicator: 65% life remaining

**Step 2: Root Cause Analysis** (Analytics → Root Cause)
- Primary Cause: "Inadequate cooling effectiveness" 
- Contributing Factors:
  - High electrical loading (35% impact, 90% confidence)
  - Elevated ambient temperature (25% impact, 80% confidence) 
  - Degraded cooling system efficiency (20% impact, 70% confidence)
- Recommended Actions:
  1. "Check cooling pump operation" (High priority, 40% impact)
  2. "Reduce electrical loading by 20%" (High priority, 35% impact)
  3. "Clean heat exchanger surfaces" (Medium priority, 25% impact)
- Timeline:
  - Immediate: Within 24 hours
  - Short-term: Within 1 week  
  - Long-term: Within 1 month

**Step 3: Option Comparison** (Analytics → What-If Scenarios)
- Scenarios ranked by predicted health score improvement:
  1. **Improve Cooling by 5°C** (RECOMMENDED)
     - Health Score: +8 points
     - RUL Change: +45 days
     - Cost Impact: -$1,200 (savings from efficiency)
  2. **Reduce Load by 20%**
     - Health Score: +6 points
     - RUL Change: +30 days
     - Cost Impact: +$2,500 (lost revenue)
  3. **Continue Operation**
     - Health Score: 0 points
     - RUL Change: 0 days
     - Cost Impact: $0

**Step 4: Constrained Optimization** (Analytics → Optimization)
- Set constraints: Budget = $10,000, Max Downtime = 2 hours, Risk Threshold = MEDIUM
- Recommended Strategy: "Improve Cooling by 5°C"
- Expected Benefits:
  - "Reduced thermal stress" (35% improvement)
  - "Lower failure risk" (40% reduction) 
  - "Energy efficiency gains" ($1,200 annual savings)
- Implementation Plan:
  - Timeline: 1-3 days
  - Resources: Maintenance crew, diagnostic tools
  - Prerequisites: Cooling system manuals, spare parts availability
- ROI Analysis:
  - Initial Cost: $1,800
  - Annual Savings: $1,200
  - Payback Period: 1.8 years

**Step 5: Action Planning**
- Schedule immediate check of cooling pump operation
- Plan load reduction for peak hours tomorrow
- Schedule heat exchanger cleaning for next maintenance window
- Monitor temperature trends to verify effectiveness

### 4. Tips for Effective Use

#### For Daily Operations
- Start each shift by checking the dashboard visualizations
- Look for sudden changes in trends rather than absolute values
- Use the Health Gauge as your first indicator of asset status
- Pay attention to correlated movements in multiple parameters

#### For Troubleshooting
- When an alert occurs, go straight to Root Cause Analysis
- Focus on the primary cause - fixing this often resolves secondary issues
- Check the confidence levels in contributing factors
- Follow recommended actions in priority order

#### For Planning and Optimization
- Use What-If Scenario Planning to compare multiple options before meetings
- Set realistic constraints in the Optimization tool (be honest about budget/time limits)
- Look for scenarios with positive cost impacts (money saved) as well as technical benefits
- Consider the implementation complexity, not just the technical effectiveness
- Use ROI calculations to build business cases for investments

#### For Reporting and Communication
- Export visualization images for inclusion in reports
- Use the clear language from analytics components in work orders
- Reference specific scenario numbers when discussing options with stakeholders
- Include confidence levels when presenting predictions to management
- Cite the remediation timeline when scheduling work

### 5. Understanding the AI Behind the Features

The advanced features leverage the same AI models that power the core Aegis platform:

**Data Sources**:
- Real-time telemetry from asset sensors
- Historical performance patterns
- Manufacturer specifications and ratings
- Engineering principles and failure mode databases
- Maintenance history and intervention outcomes

**Analytical Methods**:
- Statistical correlation analysis for trend identification
- Fault tree analysis for root cause determination
- Monte Carlo simulation for what-if scenario outcomes
- Multi-criteria decision analysis for optimization
- Constraint satisfaction algorithms for feasible solution finding

**Confidence Indicators**:
All predictive elements include confidence scores based on:
- Data quality and completeness
- Model certainty in predictions
- Historical accuracy of similar predictions
- Relevance of training data to current situation

### 6. Troubleshooting Common Issues

**"Analysis Unavailable" Messages**
- Wait a moment and refresh - the system may be calculating
- Check if backend is running (look for error banners on pages)
- Verify network connectivity to the backend server
- Try accessing a simpler page like Dashboard first

**"No Data Available" in Visualizations**
- May indicate telemetry feed interruption
- Check data freshness timestamps in the corner of charts
- Verify that the asset ID in the URL matches an existing asset
- Consider that very new assets may not have historical trends yet

**Unexpected Recommendations**
- Remember that AI optimizes for stated objectives and constraints
- Review what constraints you've set (consciously or unconsciously)
- Consider that the AI may be weighing factors you haven't considered
- Use What-If scenarios to test your preferred alternatives manually

**"Confidence Seems Low"**
- Low confidence often means conflicting data or unusual conditions
- Check contributing factors for disagreements in the data
- Consider gathering additional manual measurements for verification
- Use low confidence as a trigger for expert human review

### 7. Best Practices for Different User Roles

**Field Technicians**
- Focus on Root Cause Analysis for daily work guidance
- Use What-If scenarios to understand why certain procedures are recommended
- Check Implementation Plans for specific tool and parts requirements
- Trust high-confidence recommendations, seek guidance for low-confidence ones

**Reliability Engineers**
- Leverage What-If planning for reliability improvement projects
- Use Optimization for maintenance strategy development
- Track prediction accuracy over time to build trust in the system
- Combine AI insights with domain expertise for complex cases

**Maintenance Managers**
- Use Optimization for budget-justified maintenance planning
- Monitor ROI calculations for department performance metrics
- Use Scenario Planning for capital investment justifications
- Track recommended vs. actual actions for process improvement

**Executives and Stakeholders**
- Focus on ROI analysis and cost-benefit predictions
- Use What-If scenarios to understand risk mitigation options
- Review trending health scores for portfolio-level asset management
- Consider confidence levels when making strategic decisions

## Conclusion

The advanced visualization and analytics features transform Aegis from a reactive monitoring tool into a proactive decision intelligence system. By combining instant visual feedback with sophisticated analytical capabilities, engineers can now:

1. **See** what's happening with instant visualizations
2. **Understand** why it's happening through root cause analysis
3. **Predict** what will happen with different actions using what-if scenarios
4. **Choose** the best action considering real-world constraints through optimization
5. **Justify** decisions with clear ROI predictions and confidence levels

These capabilities enable the transition from time-based maintenance to condition-based maintenance, and from fixed scheduling to dynamic, asset-driven optimization - ultimately improving reliability, reducing costs, and extending asset life.
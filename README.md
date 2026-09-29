# Aegis - AI-Powered Decision Intelligence Platform

Aegis is an AI-powered decision intelligence platform for critical electrical infrastructure. It monitors electrical asset health, predicts degradation, simulates possible interventions through a digital twin, and recommends the safest and most cost-effective action to an engineer.

## Project Overview

This project implements a working end-to-end prototype focused on one critical electrical asset: a power transformer.

**Core Innovation**: Unlike traditional predictive maintenance systems that stop at `Observe → Predict → Alert`, Aegis goes further:
```
Observe → Predict → Simulate → Evaluate → Recommend → Explain
```

## Repository Structure

```
aegis/
├── backend/
│   ├── api/              # API endpoints and routing
│   ├── models/           # ML models for health prediction
│   │   ├── health_model.py
│   │   ├── rul_model.py
│   │   └── risk_model.py
│   ├── digital_twin/     # Transformer simulation
│   │   └── transformer.py
│   ├── decision_engine/  # Action evaluation and optimization
│   │   └── optimizer.py
│   └── simulator/        # Telemetry simulation
│       └── telemetry.py
├── frontend/
│   ├── dashboard/        # Command center view
│   ├── asset/            # Asset intelligence page
│   ├── decisions/        # Decision center page
│   └── digital-twin/     # Digital twin controls
├── data/
│   ├── telemetry/        # Sensor data storage
│   └── maintenance/      # Maintenance history
├── docs/
│   ├── architecture.md   # Detailed system architecture
│   ├── api.md            # API contract specifications
│   └── demo-script.md    # Demo presentation guide
└── README.md
```

## Getting Started

See [BUILD_LOG.md](BUILD_LOG.md) for development progress tracking.

## Team Structure

- **Person 1**: AI/Asset Health Engineer (Health scoring, failure prediction, RUL)
- **Person 2**: Digital Twin/Simulation Engineer (Transformer behavior modeling)
- **Person 3**: Decision Intelligence Engineer (Action evaluation, optimization)
- **Person 4**: Full-Stack/Product Engineer (UI, integration, UX)

## Development Phases

1. **Days 1-2**: Foundation (parameters, schema, APIs, wireframes)
2. **Days 3-5**: Parallel development (using mock data)
3. **Days 6-8**: Integration (end-to-end pipeline)
4. **Days 9-11**: Productization (realism, UI improvements)
5. **Days 12-13**: Testing (5 scenarios validation)
6. **Days 14-15**: Demo and pitch preparation

## Documentation

- [Architecture Documentation](docs/architecture.md)
- [Build Log](BUILD_LOG.md)
- [Original Project Plan](Aegis_4_Person_Hackathon_Plan.md)# Aegis-Schneider-Hackathon

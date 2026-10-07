# Aegis Platform - Quick Start Guide

## Overview
Aegis is an AI-powered decision intelligence platform for critical electrical infrastructure. It monitors transformer health, predicts degradation, simulates interventions through a digital twin, and recommends optimal actions.

## System Requirements
- Python 3.8+
- Node.js 16+
- npm or yarn
- Approximately 500MB free disk space

## Quick Start

### Option 1: Using the startup script (Recommended)
```bash
python start_aegis.py
```
This will start both backend and frontend automatically.

### Option 2: Manual Start

#### Start Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend will be available at: http://localhost:8000

#### Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: http://localhost:3000

## Platform Features
Once both services are running, you can access:

1. **Frontend Dashboard**: http://localhost:3000
   - Real-time asset monitoring
   - Health assessment visualization
   - Risk analysis breakdown
   - AI-driven intervention recommendations
   - Detailed explanations for decisions

2. **Backend API**: http://localhost:8000
   - RESTful API for all Aegis functionality
   - Interactive API documentation: http://localhost:8000/docs
   - Health assessment endpoint
   - RUL prediction endpoint
   - Risk assessment endpoint
   - Decision optimization endpoint
   - Digital twin simulation endpoint
   - Summary endpoint combining all assessments

## API Endpoints
- `GET /health` - System health check
- `POST /assets/{asset_id}/health` - Asset health assessment
- `POST /assets/{asset_id}/rul` - Remaining useful life prediction
- `POST /assets/{asset_id}/risk` - Comprehensive risk assessment
- `POST /assets/{asset_id}/decision` - Optimal intervention recommendation
- `POST /assets/{asset_id}/simulate` - Digital twin simulation
- `GET /assets/{asset_id}/summary` - Complete asset summary
- `GET /assets/{asset_id}/telemetry` - Historical telemetry data

## Sample Data
The platform comes pre-loaded with sample data demonstrating:
- Normal transformer operation
- Elevated load conditions
- Thermal stress scenarios
- Aging asset conditions
- Multiple risk factor combinations

## Stopping the Platform
To stop the platform:
- If using `start_aegis.py`: Press Ctrl+C
- If started manually: Use Ctrl+C in each terminal window

## Troubleshooting
If you encounter issues:
1. Ensure ports 8000 (backend) and 3000 (frontend) are available
2. Check that all dependencies are installed correctly
3. Verify Python and Node.js versions meet requirements
4. Check the console output for specific error messages

## Notes
- The first startup may take a moment as models initialize and train on baseline data
- Subsequent startups will be faster as trained models are reused
- For production use, consider setting up proper database storage and authentication
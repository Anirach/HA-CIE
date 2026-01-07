# Hospital Accreditation Causal Insight Engine (HA-CIE)

A comprehensive accreditation analytics platform that transforms complex hospital standards compliance data into an interactive causal knowledge graph. The system enables hospitals to track accreditation readiness over time, explore cause-effect relationships between standard requirements, simulate the impact of improvement interventions on accreditation maturity levels, and generate AI-powered insights for quality improvement.

Built upon HA Thailand Standards 5th Edition, ISQua EEA Guidelines 6th Edition, and WHO DISAH Framework.

## Features

### Core Capabilities

- **Interactive Causal Graph Visualization** - Cytoscape.js-powered graph showing relationships between accreditation criteria with color-coded nodes by domain and edge thickness representing dependency strength
- **Timeline Animation** - Animate through assessment cycles to visualize hospital progress over time with play/pause, speed control, and changes panel
- **Maturity Calculator** - Multi-factor weighted scoring across HA Thailand 5-level framework with ISQua EEA mapping
- **What-If Simulator** - Project maturity improvements with pre-built and custom scenarios, featuring both QI Team (technical) and Executive (simplified) modes
- **Compliance Dashboard** - Track trends with sparklines, domain scores, and traffic-light status system
- **AI Insights Engine** - Pattern recognition, risk assessment, gap analysis, prioritized recommendations, and Surveyor Prep module
- **PDF Report Generation** - Comprehensive reports with hospital profile, maturity assessment, gap analysis, and improvement roadmap
- **Digital Health Readiness** - WHO DISAH framework integration for tracking digital health intervention implementation
- **ISQua EEA Integration** - 9 Principles mapping with automatic HA-to-ISQua score conversion
- **Data Import** - Upload hospital data from JSON or Excel files with smart merge capabilities
- **Advanced Causal Inference** - DoWhy, pgmpy, and EconML integration for ATE estimation, counterfactual analysis, and sensitivity analysis

### Standards Framework

The system is built around the HA Thailand Standards 5th Edition structure:

- **Part I**: Organization Management Overview (20% weight)
  - Leadership, Strategy, Patient/Customer Focus, Measurement/KM, Workforce, Operations
- **Part II**: Key Hospital Systems (35% weight)
  - Quality/Risk/Safety, Professional Governance, Environment, Infection Prevention, Medical Records, Medication, Diagnostics, Surveillance, Community
- **Part III**: Patient Care Process (30% weight)
  - Access, Assessment, Planning, Care Delivery, Information, Continuity
- **Part IV**: Organization Performance Results (15% weight)
  - Healthcare Results, Patient Results, Workforce Results, Leadership Results, Process Results, Financial Results

### Accreditation Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| Pass | 2.5-2.9 | Basic accreditation achieved |
| Good | 3.0-3.4 | Solid quality systems in place |
| Very Good | 3.5-3.9 | Strong continuous improvement culture |
| Excellent | 4.0+ | Role model organization |

## Technology Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS v4
- Cytoscape.js (graph visualization)
- Recharts (charts)
- Zustand (state management)
- React Query (data fetching)
- Lucide React (icons)

### Backend
- FastAPI (Python 3.11+)
- Pydantic v2 (validation)
- SQLAlchemy 2.0 (ORM)
- NetworkX (graph algorithms)
- DoWhy (causal inference)
- pgmpy (Bayesian networks)
- EconML (treatment effects)

### Database
- PostgreSQL 16 (primary storage)
- Neo4j 5 (graph database)
- JSON Mode (development fallback)

### Deployment
- Docker + Docker Compose

## Quick Start

### Prerequisites

**Docker (Recommended)**
- Docker and Docker Compose installed

**Local Development**
- Node.js 18+
- Python 3.11+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd HA-CIE
```

2. Run the setup script:

**Using Docker (recommended for full setup):**
```bash
./init.sh --docker
```

**Local development (JSON fallback mode):**
```bash
./init.sh --dev
```

**Install dependencies only:**
```bash
./init.sh --install-only
```

3. Access the application:
- Frontend: http://localhost:3500
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474 (Docker mode only)

### Manual Startup

If you used `--install-only`, start the servers manually:

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

## Project Structure

```
HA-CIE/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── store/           # Zustand state stores
│   │   ├── api/             # API client functions
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   └── package.json
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API routes
│   │   │   └── v1/          # Version 1 endpoints
│   │   ├── core/            # Core configuration
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utility functions
│   ├── tests/               # Backend tests
│   └── requirements.txt
├── data/                     # JSON data storage (dev mode)
├── docker/                   # Docker configuration files
├── docker-compose.yml        # Docker Compose configuration
├── init.sh                   # Setup script
└── README.md
```

## API Endpoints

### Hospitals
- `GET /api/v1/hospitals` - List all hospitals
- `GET /api/v1/hospitals/{id}` - Get hospital details
- `POST /api/v1/hospitals` - Create hospital
- `PATCH /api/v1/hospitals/{id}` - Update hospital
- `DELETE /api/v1/hospitals/{id}` - Delete hospital
- `POST /api/v1/hospitals/upload` - Upload hospital data (JSON/Excel)

### Assessments
- `GET /api/v1/hospitals/{id}/assessments` - List hospital assessments
- `GET /api/v1/hospitals/{id}/assessments/{assessment_id}` - Get assessment
- `POST /api/v1/hospitals/{id}/assessments` - Create assessment
- `DELETE /api/v1/hospitals/{id}/assessments/{assessment_id}` - Delete assessment

### Graph
- `GET /api/v1/hospitals/{id}/graph` - Get hospital graph data
- `GET /api/v1/graph/standards` - Get standards framework graph

### Dashboard
- `GET /api/v1/hospitals/{id}/dashboard` - Get dashboard data
- `GET /api/v1/hospitals/{id}/trends` - Get trend data

### Simulations
- `POST /api/v1/simulations` - Run what-if simulation
- `GET /api/v1/simulations/scenarios` - Get pre-built scenarios
- `GET /api/v1/simulations/{id}` - Get simulation results

### Reports
- `GET /api/v1/reports/{hospital_id}/pdf` - Download PDF report
- `GET /api/v1/reports/{hospital_id}/html` - Preview HTML report

### AI Insights
- `POST /api/v1/insights/{hospital_id}` - Generate insights
- `GET /api/v1/insights/{hospital_id}/gaps` - Get gap analysis
- `GET /api/v1/insights/{hospital_id}/risks` - Get risk assessment
- `GET /api/v1/insights/{hospital_id}/recommendations` - Get recommendations
- `DELETE /api/v1/insights/{hospital_id}/cache` - Clear insights cache

### Causal Inference
- `POST /api/v1/causal/estimate-effect` - Estimate treatment effect
- `POST /api/v1/causal/counterfactual` - Counterfactual analysis
- `POST /api/v1/causal/root-cause` - Root cause analysis
- `POST /api/v1/causal/cascade` - Analyze cascade effects
- `GET /api/v1/causal/methods` - Available estimation methods

### Digital Health (WHO DISAH Framework)
- `GET /api/v1/digital-health/framework` - Get DISAH framework structure
- `GET /api/v1/digital-health/categories/{id}` - Get category details
- `POST /api/v1/digital-health/assess` - Assess digital health readiness
- `GET /api/v1/digital-health/assessment/{hospital_id}` - Get assessment results
- `GET /api/v1/digital-health/ha-alignment` - Get HA-to-DISAH mapping
- `GET /api/v1/digital-health/readiness-levels` - Get readiness level definitions

### ISQua EEA Integration
- `GET /api/v1/isqua/principles` - Get 9 ISQua principles
- `GET /api/v1/isqua/principles/{id}` - Get principle details
- `GET /api/v1/isqua/ha-mapping` - Get HA-to-ISQua mapping
- `POST /api/v1/isqua/assess` - Assess ISQua compliance
- `GET /api/v1/isqua/convert/ha-to-isqua` - Convert HA score to ISQua rating
- `GET /api/v1/isqua/convert/isqua-to-ha` - Convert ISQua rating to HA score

### Health
- `GET /health` - Health check endpoint

## User Roles

### QI Team Member
Full access to technical interfaces including:
- All technical visualizations
- Causal inference tools
- Full simulation parameters
- Cascade depth indicators
- Confidence intervals

### Executive
Simplified strategic interface including:
- High-level maturity scores
- Plain-language explanations
- Risk indicators
- Executive reports

## Development

### Running Tests

**Backend:**
```bash
cd backend
source venv/bin/activate
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

### Code Quality

**Backend linting:**
```bash
cd backend
source venv/bin/activate
ruff check .
```

**Frontend linting:**
```bash
cd frontend
npm run lint
```

## Configuration

### Environment Variables

Backend environment variables (`.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_MODE` | `json` or `postgres` | `json` |
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `NEO4J_URI` | Neo4j connection URI | - |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | - |
| `DEBUG` | Debug mode | `false` |
| `SECRET_KEY` | Application secret key | - |

## References

- HA Thailand Standards 5th Edition - Healthcare Accreditation Institute (Public Organization), 2022
- ISQua EEA Guidelines 6th Edition - International Society for Quality in Health Care, 2025
- WHO DISAH Framework - Classification of Digital Health Interventions, Services and Applications in Health, 2023
- Malcolm Baldrige National Quality Award - MBNQA quality framework
- Thailand Hospital Indicator Program - THIP benchmarking
- WHO Global Patient Safety Action Plan 2021-2030

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions, please contact the development team.

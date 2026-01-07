#!/bin/bash

# Hospital Accreditation Causal Insight Engine (HA-CIE)
# Initialization and Development Environment Setup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Hospital Accreditation Causal Insight Engine${NC}"
echo -e "${BLUE}  HA-CIE Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Parse arguments
USE_DOCKER=false
DEV_MODE=false
INSTALL_ONLY=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --docker) USE_DOCKER=true ;;
        --dev) DEV_MODE=true ;;
        --install-only) INSTALL_ONLY=true ;;
        --help|-h)
            echo "Usage: ./init.sh [options]"
            echo ""
            echo "Options:"
            echo "  --docker        Use Docker Compose for all services"
            echo "  --dev           Development mode (JSON fallback, no Docker)"
            echo "  --install-only  Only install dependencies, don't start servers"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Service URLs (when running):"
            echo "  Frontend:       http://localhost:3500"
            echo "  Backend API:    http://localhost:8000"
            echo "  API Docs:       http://localhost:8000/docs"
            echo "  Neo4j Browser:  http://localhost:7474"
            exit 0
            ;;
        *) print_error "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Check prerequisites based on mode
if [ "$USE_DOCKER" = true ]; then
    print_status "Checking Docker prerequisites..."

    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi

    print_status "Docker prerequisites met."
else
    print_status "Checking local development prerequisites..."

    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18+."
        exit 1
    fi

    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ required. Found version $(node -v)"
        exit 1
    fi
    print_status "Node.js $(node -v) found."

    # Check npm
    if ! command_exists npm; then
        print_error "npm is not installed."
        exit 1
    fi
    print_status "npm $(npm -v) found."

    # Check Python
    if command_exists python3; then
        PYTHON_CMD=python3
    elif command_exists python; then
        PYTHON_CMD=python
    else
        print_error "Python is not installed. Please install Python 3.11+."
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        print_error "Python 3.11+ required. Found version $PYTHON_VERSION"
        exit 1
    fi
    print_status "Python $PYTHON_VERSION found."

    # Check pip
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_error "pip is not installed."
        exit 1
    fi
    print_status "pip found."
fi

# Create project directory structure if it doesn't exist
print_status "Setting up project structure..."

mkdir -p frontend/src/{components,pages,hooks,store,api,types,utils}
mkdir -p frontend/public
mkdir -p backend/app/{api,core,models,schemas,services,utils}
mkdir -p backend/app/api/v1
mkdir -p backend/tests
mkdir -p data
mkdir -p docker

print_status "Project structure created."

# Setup based on mode
if [ "$USE_DOCKER" = true ]; then
    print_status "Setting up Docker environment..."

    # Create docker-compose.yml if it doesn't exist
    if [ ! -f docker-compose.yml ]; then
        cat > docker-compose.yml << 'DOCKER_EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3500:3500"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://hacie:hacie_password@postgres:5432/hacie
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=hacie_neo4j_password
      - STORAGE_MODE=postgres
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    volumes:
      - ./backend:/app

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=hacie
      - POSTGRES_PASSWORD=hacie_password
      - POSTGRES_DB=hacie
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hacie"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    environment:
      - NEO4J_AUTH=neo4j/hacie_neo4j_password
      - NEO4J_PLUGINS=["apoc"]
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD-SHELL", "wget -q --spider http://localhost:7474 || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  neo4j_data:
DOCKER_EOF
        print_status "docker-compose.yml created."
    fi

    if [ "$INSTALL_ONLY" = false ]; then
        print_status "Starting Docker services..."

        if docker compose version >/dev/null 2>&1; then
            docker compose up -d --build
        else
            docker-compose up -d --build
        fi

        print_status "Docker services started."
    fi

else
    # Local development setup

    # Frontend setup
    print_status "Setting up frontend..."

    if [ ! -f frontend/package.json ]; then
        cd frontend

        # Initialize package.json
        cat > package.json << 'PKG_EOF'
{
  "name": "ha-cie-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --port 3500",
    "build": "tsc && vite build",
    "preview": "vite preview --port 3500",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "cytoscape": "^3.28.0",
    "recharts": "^2.10.0",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.0",
    "lucide-react": "^0.294.0",
    "axios": "^1.6.2",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@types/cytoscape": "^3.19.13",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.3.2",
    "vite": "^5.0.7",
    "eslint": "^8.55.0",
    "@typescript-eslint/eslint-plugin": "^6.13.2",
    "@typescript-eslint/parser": "^6.13.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5"
  }
}
PKG_EOF

        # Create vite.config.ts
        cat > vite.config.ts << 'VITE_EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3500,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
VITE_EOF

        # Create tsconfig.json
        cat > tsconfig.json << 'TS_EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
TS_EOF

        # Create tsconfig.node.json
        cat > tsconfig.node.json << 'TSNODE_EOF'
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
TSNODE_EOF

        # Create tailwind.config.js
        cat > tailwind.config.js << 'TW_EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'part-1': '#9333ea', // purple for Organization Management
        'part-2': '#dc2626', // red for Hospital Systems
        'part-3': '#16a34a', // green for Patient Care
        'part-4': '#2563eb', // blue for Results
        'status-excellent': '#16a34a',
        'status-good': '#eab308',
        'status-needs-improvement': '#f97316',
        'status-critical': '#dc2626',
      },
    },
  },
  plugins: [],
}
TW_EOF

        # Create postcss.config.js
        cat > postcss.config.js << 'POSTCSS_EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
POSTCSS_EOF

        # Create index.html
        cat > index.html << 'HTML_EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>HA-CIE - Hospital Accreditation Causal Insight Engine</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML_EOF

        # Create basic src files
        mkdir -p src

        cat > src/main.tsx << 'MAIN_EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
MAIN_EOF

        cat > src/App.tsx << 'APP_EOF'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <main className="container mx-auto p-4">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Hospital Accreditation Causal Insight Engine
            </h1>
            <p className="text-gray-600">
              Welcome to HA-CIE. The application is being set up.
            </p>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
APP_EOF

        cat > src/index.css << 'CSS_EOF'
@import "tailwindcss";

/* Custom styles for HA-CIE */
:root {
  --color-part-1: #9333ea;
  --color-part-2: #dc2626;
  --color-part-3: #16a34a;
  --color-part-4: #2563eb;
}
CSS_EOF

        cd ..
        print_status "Frontend configuration files created."
    fi

    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..

    # Backend setup
    print_status "Setting up backend..."

    if [ ! -f backend/requirements.txt ]; then
        cat > backend/requirements.txt << 'REQ_EOF'
# FastAPI and Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
asyncpg==0.29.0
neo4j==5.16.0
alembic==1.13.1

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# Graph and Analytics
networkx==3.2.1
numpy==1.26.3
pandas==2.1.4

# Causal Inference
dowhy==0.11.1
pgmpy==0.1.24
econml==0.14.1
scikit-learn==1.4.0

# PDF Generation
reportlab==4.0.8
weasyprint==60.2

# Utilities
python-dotenv==1.0.0
httpx==0.26.0
aiofiles==23.2.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
REQ_EOF
        print_status "requirements.txt created."
    fi

    # Create Python virtual environment
    if [ ! -d backend/venv ]; then
        print_status "Creating Python virtual environment..."
        cd backend
        $PYTHON_CMD -m venv venv
        cd ..
    fi

    # Install backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    cd ..

    # Create backend main.py if it doesn't exist
    if [ ! -f backend/app/main.py ]; then
        cat > backend/app/__init__.py << 'INIT_EOF'
# HA-CIE Backend Application
INIT_EOF

        cat > backend/app/main.py << 'MAIN_PY_EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hospital Accreditation Causal Insight Engine",
    description="API for hospital accreditation analytics and causal inference",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "storage_mode": "json",  # Will be updated when DB is configured
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to HA-CIE API",
        "docs_url": "/docs",
    }
MAIN_PY_EOF
        print_status "Backend main.py created."
    fi

    # Create .env file for local development
    if [ ! -f backend/.env ]; then
        cat > backend/.env << 'ENV_EOF'
# HA-CIE Backend Environment Configuration

# Storage Mode: 'json' for development, 'postgres' for production
STORAGE_MODE=json

# PostgreSQL (for production)
DATABASE_URL=postgresql://hacie:hacie_password@localhost:5432/hacie

# Neo4j Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=hacie_neo4j_password

# Application Settings
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Data Directory (for JSON mode)
DATA_DIR=../data
ENV_EOF
        print_status ".env file created."
    fi
fi

# Print summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$INSTALL_ONLY" = true ]; then
    echo -e "Dependencies installed. To start the application, run:"
    echo ""
    if [ "$USE_DOCKER" = true ]; then
        echo -e "  ${BLUE}docker compose up${NC}"
    else
        echo -e "  ${BLUE}# Terminal 1 - Backend:${NC}"
        echo -e "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
        echo ""
        echo -e "  ${BLUE}# Terminal 2 - Frontend:${NC}"
        echo -e "  cd frontend && npm run dev"
    fi
else
    if [ "$USE_DOCKER" = true ]; then
        echo -e "Services are starting via Docker Compose."
    else
        echo -e "To start the application:"
        echo ""
        echo -e "  ${BLUE}# Terminal 1 - Backend:${NC}"
        echo -e "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
        echo ""
        echo -e "  ${BLUE}# Terminal 2 - Frontend:${NC}"
        echo -e "  cd frontend && npm run dev"
    fi
fi

echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "  Frontend:       http://localhost:3500"
echo -e "  Backend API:    http://localhost:8000"
echo -e "  API Docs:       http://localhost:8000/docs"
if [ "$USE_DOCKER" = true ]; then
    echo -e "  Neo4j Browser:  http://localhost:7474"
fi
echo ""
echo -e "${YELLOW}Note: For production deployment, update the .env file with secure credentials.${NC}"
echo ""

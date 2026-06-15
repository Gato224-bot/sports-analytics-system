# Sports Analytics System

**Senior Data Engineering & Science Consultancy Project**

Un sistema de análisis de datos deportivos basado en **principios estadísticos rigurosos**, **Software Engineering limpio** y **metodología científica reproducible**.

---

## 🎯 Objetivo

Construir una herramienta técnica que optimice la toma de decisiones basada en métricas estadísticas, validando la capacidad de procesar datos en entornos de alta incertidumbre.

**NO es un sistema de apuestas. Es una plataforma de análisis que demuestra:**
- Limpieza y transformación de datos en pipelines escalables
- Modelado predictivo con validación estadística rigurosa
- Backtesting con significancia estadística (p-value < 0.05)
- Ingeniería de software profesional (Clean Code, CI/CD, versionamiento)

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────��──────────────────────┐
│           SPORTS ANALYTICS SYSTEM ARCHITECTURE           │
└─────────────────────────────────────────────────────────┘

LAYER 1: INGESTION & STORAGE
├── Data Sources: APIs (football-data.org), Web Scraping
└── Data Lake: PostgreSQL + TimescaleDB

LAYER 2: PROCESSING (ETL/ELT)
├── Orchestration: Apache Airflow / Prefect
├── Language: Python 3.11+
└── Libraries: pandas, polars, sqlalchemy, pydantic

LAYER 3: MODELING & STATISTICS
├── EDA: Jupyter Notebook
├── Statistics: scipy.stats, statsmodels
├── ML: XGBoost, LightGBM, scikit-learn
└── Model Registry: MLflow

LAYER 4: VISUALIZATION & DASHBOARDS
├── Interactive: Plotly, Seaborn
├── MVP Dashboard: Streamlit
└── BI: Metabase (production)

LAYER 5: INFRASTRUCTURE & DEPLOYMENT
├── Version Control: Git + GitHub
├── CI/CD: GitHub Actions
├── Containerization: Docker + docker-compose
└── Deployment: Render.com / Railway
```

---

## 📁 Estructura de Carpetas

```
sports_analytics_system/
├── .github/
│   └── workflows/
│       ├── tests.yml          # Automated testing on push
│       └── deploy.yml         # CD pipeline
├── data/
│   ├── raw/                   # NEVER MODIFY - raw from APIs
│   ├── processed/             # After validation & cleaning
│   └── features/              # Feature engineering outputs
├── src/
│   ├── __init__.py
│   ├── config.py              # Global config, connections
│   ├── schemas/
│   │   ├── raw_schema.py      # Pydantic models for validation
│   │   └── feature_schema.py
│   ├── extraction/
│   │   ├── api_fetcher.py     # Fetch from APIs
│   │   └── scraper.py         # Web scraping
│   ├── transformation/
│   │   ├── validator.py       # Great Expectations gates
│   │   ├── cleaner.py         # Cleaning & outlier detection
│   │   └── features.py        # Feature engineering
│   ├── models/
│   │   ├── baseline.py        # Simple baseline models
│   │   ├── advanced.py        # XGBoost, LightGBM
│   │   └── evaluation.py      # Backtesting framework
│   └── visualization/
│       └── dashboard.py       # Streamlit app
├── tests/
│   ├── test_schemas.py
│   ├── test_cleaner.py
│   ├── test_models.py
│   └── conftest.py            # pytest fixtures
├── notebooks/
│   └── 01_eda.ipynb           # Exploratory Data Analysis
├── dags/
│   └── airflow_pipeline.py    # Airflow DAG definitions
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .gitignore
├── setup.py
└── Makefile
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Gato224-bot/sports-analytics-system.git
cd sports-analytics-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and DB credentials
```

### 3. Initialize Database
```bash
python -m src.config --init-db
```

### 4. Run Tests
```bash
pytest tests/ -v --cov=src
```

### 5. Start Streamlit Dashboard
```bash
streamlit run src/visualization/dashboard.py
```

---

## 📊 Data Pipeline Flow

```
raw_data 
    ↓ [API Fetch / Scrape]
validation 
    ↓ [Pydantic Schema Check]
cleaning 
    ↓ [Outliers, Duplicates, Missing Values]
feature_engineering 
    ↓ [Domain Logic, Rolling Averages, H2H]
training 
    ↓ [Train/Test Split, Cross-Validation]
evaluation 
    ↓ [Backtesting, Statistical Significance]
serving 
    ↓ [API, Dashboard, MLflow Registry]
```

---

## 🔬 Key Principles

### 1. **No Guessing, Only Calculation**
- Every decision grounded in p-values, confidence intervals, or Expected Value
- Binomial tests for model significance
- Log-loss for probability calibration

### 2. **Complete Auditability**
- Every data transformation tracked (timestamp, version, user)
- Data lineage from raw → processed → features
- Model versioning in MLflow

### 3. **Reproducibility**
- Same code + data = same result, always
- Seed management for random processes
- Docker for environment consistency

### 4. **Clean Code**
- PEP 8 compliance (enforced by black + flake8)
- Type hints throughout
- Docstrings for every function
- Unit tests (pytest)

### 5. **Separation of Concerns**
- ETL (data) ≠ ML (models) ≠ BI (reports)
- Modular architecture
- Clear interfaces between layers

---

## 📈 Validation Strategy

### Minimum Data Requirements
- **500+ matches** from 3+ seasons
- **10+ features** per match (stats, H2H, context)
- **Time-series validation** (walk-forward, not random split)

### Statistical Testing
```
Metric                   Threshold          Description
─────────────────────────────────────────────────────────
Binomial Test p-value    < 0.05            Model > random
Log Loss Improvement     > 1.05x            Better calibration
Walk-Forward Accuracy    > 33.33%           Better than random
Expected Value           > 0                Math positive
```

### Error Budget
```
Stage              Tolerance          Control
──────────────────────────────────────────────────────
Data Validation    < 2% rejection      Great Expectations
Cleaning           < 1% data loss      Audit logs
Feature Eng.       < 5% correlation    VIF < 5
Model Training     < 2% overfitting    Learning curves
Backtesting        p < 0.05            Statistical test
Deployment         > +10% vs baseline  Monitoring
```

---

## 🛠️ Tech Stack

### Core
- **Python 3.11+** with type hints
- **PostgreSQL 13+** with TimescaleDB

### Data Processing
- `pandas`, `polars` - Data manipulation
- `sqlalchemy` - ORM
- `pydantic` - Schema validation
- `great-expectations` - Data quality gates

### Statistics & ML
- `scipy.stats` - Statistical tests
- `scikit-learn` - ML utilities
- `xgboost`, `lightgbm`, `catboost` - Advanced models
- `statsmodels` - Time series & inference

### Visualization
- `plotly` - Interactive charts
- `seaborn` - Statistical plots
- `streamlit` - Dashboard MVP

### MLOps
- `mlflow` - Model registry & tracking
- `airflow` / `prefect` - Workflow orchestration

### DevOps
- `docker` - Containerization
- `pytest` - Testing framework
- `black`, `flake8`, `mypy` - Code quality

---

## 📋 Development Phases

### Phase 1: Foundation (Weeks 1-2)
- [x] Repository structure
- [ ] GitHub Actions CI/CD
- [ ] PostgreSQL + schemas
- [ ] Unit tests framework
- **Deliverable**: Functional repo with automated testing

### Phase 2: Ingestion (Weeks 3-4)
- [ ] API integration
- [ ] Data cleaner implementation
- [ ] Feature engineering pipeline
- [ ] Streamlit MVP dashboard
- **Deliverable**: 500+ matches in PostgreSQL

### Phase 3: Modeling (Weeks 5-8)
- [ ] EDA notebook
- [ ] Baseline model (logistic regression)
- [ ] Backtesting framework
- [ ] Statistical significance validation
- [ ] Hyperparameter tuning (XGBoost)
- [ ] Walk-forward validation
- **Deliverable**: Model with p-value < 0.05

### Phase 4: Productionization (Weeks 9-10)
- [ ] MLflow integration
- [ ] FastAPI endpoints
- [ ] Metabase dashboards
- [ ] Model monitoring & retraining
- [ ] Docker deployment
- **Deliverable**: Production-ready system

---

## 🔒 Ethical & Legal Boundaries

**This project is strictly for:**
- ✅ Data engineering & science skill demonstration
- ✅ Statistical model validation
- ✅ Software architecture best practices
- ✅ Portfolio building

**This project is NOT for:**
- ❌ Betting recommendations
- ❌ Financial gain prediction
- ❌ Manipulation of gambling systems
- ❌ Circumventing platform terms of service

---

## 📖 Documentation

- [Data Dictionary](./docs/DATA_DICTIONARY.md) - Feature definitions
- [API Reference](./docs/API.md) - Endpoint documentation
- [Model Card](./docs/MODEL_CARD.md) - Model specifications
- [Deployment Guide](./docs/DEPLOYMENT.md) - Production runbook

---

## 🤝 Contributing

This is a single-developer portfolio project under senior consultancy. Guidelines:
- Follow PEP 8 + type hints
- Write tests for new features
- Document all functions
- Update this README for architectural changes

---

## 📜 License

MIT License - See LICENSE file

---

## 📞 Contact

**Project Lead**: Gato224-bot  
**Consultancy Focus**: Data Engineering, Statistical Modeling, Software Architecture

---

**Last Updated**: 2026-06-15  
**Status**: In Development (Phase 1)

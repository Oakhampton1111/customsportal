# Digital Ocean Deployment Guide - Customs Broker Portal

## Overview
Complete deployment guide for migrating the Customs Broker Portal from local SQLite to production PostgreSQL on Digital Ocean.

## 🏗️ Infrastructure Setup

### 1. Digital Ocean Resources Required

#### Droplet Configuration
- **App Platform**: For containerized deployment
- **Database**: Managed PostgreSQL 15+
- **Spaces**: For static file storage (optional)
- **Load Balancer**: For high availability (optional)

#### Recommended Specifications
```
Production Environment:
- App Platform: Professional ($12/month)
- Database: Basic PostgreSQL ($15/month, 1GB RAM, 10GB storage)
- Total: ~$27/month

Staging Environment:
- App Platform: Basic ($5/month)  
- Database: Development PostgreSQL ($7/month, 512MB RAM, 1GB storage)
- Total: ~$12/month
```

### 2. Database Migration Strategy

#### Phase 1: PostgreSQL Setup
1. Create managed PostgreSQL database on Digital Ocean
2. Configure connection pooling and security
3. Run schema creation
4. Migrate data from SQLite

#### Phase 2: Application Deployment
1. Containerize backend and frontend
2. Deploy to App Platform
3. Configure environment variables
4. Set up monitoring and logging

## 📊 SQLite to PostgreSQL Migration

### Migration Script
```python
# migration/sqlite_to_postgres.py
import asyncio
import sqlite3
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Any

class DatabaseMigrator:
    def __init__(self, sqlite_path: str, postgres_url: str):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        
    async def migrate_all_data(self):
        """Complete migration from SQLite to PostgreSQL"""
        
        # Connect to both databases
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        
        postgres_conn = await asyncpg.connect(self.postgres_url)
        
        try:
            print("Starting database migration...")
            
            # Migration order (respecting foreign key dependencies)
            migration_order = [
                'tariff_sections',
                'tariff_chapters', 
                'trade_agreements',
                'tariff_codes',
                'duty_rates',
                'fta_rates',
                'dumping_duties',
                'tcos',
                'gst_provisions',
                'export_codes',
                'product_classifications'
            ]
            
            for table_name in migration_order:
                await self.migrate_table(sqlite_conn, postgres_conn, table_name)
                
            print("Migration completed successfully!")
            
        finally:
            sqlite_conn.close()
            await postgres_conn.close()
    
    async def migrate_table(self, sqlite_conn, postgres_conn, table_name: str):
        """Migrate a single table"""
        print(f"Migrating table: {table_name}")
        
        # Get data from SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  No data found in {table_name}")
            return
            
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Prepare PostgreSQL insert
        placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
        columns_str = ', '.join(columns)
        
        insert_query = f"""
            INSERT INTO {table_name} ({columns_str}) 
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        # Convert rows to list of tuples
        data_rows = []
        for row in rows:
            # Handle JSON fields and data type conversions
            converted_row = []
            for i, value in enumerate(row):
                if value is None:
                    converted_row.append(None)
                elif isinstance(value, str) and value.startswith('{'):
                    # Try to parse JSON
                    try:
                        converted_row.append(json.loads(value))
                    except:
                        converted_row.append(value)
                else:
                    converted_row.append(value)
            data_rows.append(tuple(converted_row))
        
        # Batch insert into PostgreSQL
        await postgres_conn.executemany(insert_query, data_rows)
        
        print(f"  Migrated {len(data_rows)} rows to {table_name}")

# Usage
async def run_migration():
    migrator = DatabaseMigrator(
        sqlite_path="backend/customs_portal.db",
        postgres_url="postgresql://user:pass@host:5432/customs_broker_portal"
    )
    await migrator.migrate_all_data()

if __name__ == "__main__":
    asyncio.run(run_migration())
```

### Data Validation Script
```python
# migration/validate_migration.py
import asyncio
import sqlite3
import asyncpg

async def validate_migration(sqlite_path: str, postgres_url: str):
    """Validate that migration was successful"""
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    postgres_conn = await asyncpg.connect(postgres_url)
    
    tables = [
        'tariff_codes', 'duty_rates', 'fta_rates', 'dumping_duties',
        'tcos', 'gst_provisions', 'export_codes', 'product_classifications',
        'tariff_sections', 'tariff_chapters', 'trade_agreements'
    ]
    
    validation_results = {}
    
    for table in tables:
        # Count rows in SQLite
        sqlite_count = sqlite_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        
        # Count rows in PostgreSQL
        postgres_count = await postgres_conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        
        validation_results[table] = {
            'sqlite_count': sqlite_count,
            'postgres_count': postgres_count,
            'match': sqlite_count == postgres_count
        }
        
        print(f"{table}: SQLite={sqlite_count}, PostgreSQL={postgres_count}, Match={sqlite_count == postgres_count}")
    
    sqlite_conn.close()
    await postgres_conn.close()
    
    return validation_results
```

## 🐳 Docker Configuration

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose for Local Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: customs_broker_portal
      POSTGRES_USER: customs_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U customs_user -d customs_broker_portal"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://customs_user:${POSTGRES_PASSWORD}@postgres:5432/customs_broker_portal
      - ENVIRONMENT=production
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
```

## 🚀 Digital Ocean App Platform Configuration

### App Spec (app.yaml)
```yaml
name: customs-broker-portal
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/customs-broker-portal
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: ENVIRONMENT
    value: production
  - key: ANTHROPIC_API_KEY
    value: ${ANTHROPIC_API_KEY}
    type: SECRET
  - key: SECRET_KEY
    value: ${SECRET_KEY}
    type: SECRET
  - key: CORS_ORIGINS
    value: https://customs-broker-portal.ondigitalocean.app
  health_check:
    http_path: /health
  http_port: 8000
  routes:
  - path: /api
  - path: /docs
  - path: /health

- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/customs-broker-portal
    branch: main
  build_command: npm run build
  run_command: npm run preview -- --host 0.0.0.0 --port $PORT
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: VITE_API_URL
    value: https://customs-broker-portal.ondigitalocean.app
  http_port: 8080
  routes:
  - path: /

databases:
- name: db
  engine: PG
  version: "15"
  size: basic-xs
  num_nodes: 1
```

## 🔧 Environment Configuration

### Production Environment Variables
```bash
# .env.production
# Database
DATABASE_URL=postgresql+asyncpg://username:password@host:25060/customs_broker_portal?sslmode=require

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
APP_NAME=Customs Broker Portal API
APP_VERSION=1.0.0

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=https://your-domain.com,https://customs-broker-portal.ondigitalocean.app
CORS_ALLOW_CREDENTIALS=true

# AI Integration
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=4000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Database Connection Pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_ENABLED=true
```

### Frontend Environment Variables
```bash
# frontend/.env.production
VITE_API_URL=https://customs-broker-portal.ondigitalocean.app
VITE_ENVIRONMENT=production
VITE_APP_NAME=Customs Broker Portal
VITE_APP_VERSION=1.0.0
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Create Digital Ocean account and project
- [ ] Set up managed PostgreSQL database
- [ ] Configure database firewall rules
- [ ] Create App Platform application
- [ ] Set up GitHub repository integration
- [ ] Configure environment variables and secrets

### Database Migration
- [ ] Export data from SQLite using migration script
- [ ] Run schema creation on PostgreSQL
- [ ] Import data to PostgreSQL
- [ ] Validate data integrity
- [ ] Test database connections
- [ ] Configure connection pooling

### Application Deployment
- [ ] Push code to GitHub repository
- [ ] Configure App Platform build settings
- [ ] Deploy backend service
- [ ] Deploy frontend service
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificates
- [ ] Configure health checks

### Post-Deployment
- [ ] Verify all API endpoints work
- [ ] Test frontend functionality
- [ ] Monitor application logs
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Document deployment process

## 🔍 Monitoring and Maintenance

### Health Checks
```python
# backend/health_checks.py
from fastapi import APIRouter
from database import health_check as db_health_check

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check for Digital Ocean monitoring"""
    
    db_status = await db_health_check()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "production",
        "database": db_status["database"],
        "services": {
            "api": "healthy",
            "ai": "healthy" if anthropic_api_key else "disabled"
        }
    }
```

### Logging Configuration
```python
# backend/logging_config.py
import structlog
import logging.config

def configure_logging():
    """Configure structured logging for production"""
    
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
        }
    })
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

## 💰 Cost Optimization

### Resource Sizing
- Start with basic instances and scale up based on usage
- Use managed database for reliability and maintenance
- Consider CDN for static assets if needed
- Monitor resource usage and optimize accordingly

### Estimated Monthly Costs
```
Production Environment:
- App Platform (Professional): $12/month
- PostgreSQL (Basic): $15/month  
- Domain (optional): $12/year
- Total: ~$27/month

Development/Staging:
- App Platform (Basic): $5/month
- PostgreSQL (Development): $7/month
- Total: ~$12/month
```

## 🔐 Security Considerations

### Database Security
- Use managed PostgreSQL with automatic backups
- Enable SSL connections
- Configure firewall rules
- Use strong passwords and rotate regularly

### Application Security
- Use environment variables for secrets
- Enable CORS with specific origins
- Implement rate limiting
- Use HTTPS for all connections
- Regular security updates

### Monitoring
- Set up log aggregation
- Monitor for unusual access patterns
- Configure alerts for errors and downtime
- Regular security audits

This deployment guide provides a complete path from local SQLite development to production PostgreSQL on Digital Ocean with proper security, monitoring, and maintenance procedures.

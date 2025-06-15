# 🚀 Customs Broker Portal - Digital Ocean Deployment

## Overview

This directory contains all the necessary files and scripts to deploy the Customs Broker Portal to Digital Ocean App Platform with a managed PostgreSQL database.

## 📁 Files Overview

- **`digital-ocean-setup.md`** - Comprehensive deployment guide with detailed instructions
- **`DEPLOYMENT_CHECKLIST.md`** - Step-by-step checklist for deployment process
- **`deploy.sh`** - Automated deployment script (Linux/macOS)
- **`app.yaml`** - Digital Ocean App Platform configuration
- **Migration Scripts:**
  - **`../migration/sqlite_to_postgres.py`** - Database migration script
- **Docker Configuration:**
  - **`../backend/Dockerfile`** - Backend container configuration
  - **`../frontend/Dockerfile`** - Frontend container configuration
  - **`../docker-compose.yml`** - Local development with PostgreSQL

## 🚀 Quick Start

### Prerequisites
1. Digital Ocean account with billing enabled
2. GitHub repository with your code
3. `doctl` CLI tool installed and authenticated
4. SQLite database with existing data (`backend/customs_portal.db`)

### Automated Deployment (Linux/macOS)
```bash
# Make script executable (Linux/macOS only)
chmod +x deployment/deploy.sh

# Run deployment script
./deployment/deploy.sh
```

### Manual Deployment (Windows/All Platforms)
Follow the detailed steps in `DEPLOYMENT_CHECKLIST.md`

## 📊 Database Migration

The migration process transfers all data from your local SQLite database to PostgreSQL:

```bash
# Install migration dependencies
pip install asyncpg

# Run migration
python migration/sqlite_to_postgres.py backend/customs_portal.db "postgresql://user:pass@host:5432/db"

# Validate migration
python migration/validate_migration.py
```

## 🐳 Local Development with PostgreSQL

Test your application locally with PostgreSQL before deployment:

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Set DATABASE_URL to PostgreSQL

# Start local PostgreSQL
docker-compose up postgres -d

# Run migration
python migration/sqlite_to_postgres.py

# Start application
docker-compose up
```

## 🔧 Configuration

### Environment Variables
Key environment variables for production:

```bash
# Database (automatically set by Digital Ocean)
DATABASE_URL=postgresql+asyncpg://user:pass@host:25060/db?sslmode=require

# Security
SECRET_KEY=your-secure-secret-key
ANTHROPIC_API_KEY=your-anthropic-key

# Application
ENVIRONMENT=production
CORS_ORIGINS=https://your-domain.com
```

### App Platform Configuration
The `app.yaml` file defines:
- Backend service (Python/FastAPI)
- Frontend service (Node.js/React)
- PostgreSQL database
- Environment variables
- Health checks

## 📈 Estimated Costs

### Production Environment
- **App Platform Professional**: $12/month
- **PostgreSQL Basic**: $15/month
- **Total**: ~$27/month

### Development Environment
- **App Platform Basic**: $5/month
- **PostgreSQL Development**: $7/month
- **Total**: ~$12/month

## 🔍 Monitoring

### Health Checks
- Backend: `https://your-app.ondigitalocean.app/health`
- Frontend: `https://your-app.ondigitalocean.app/`
- Database: Automatic monitoring by Digital Ocean

### Logging
```bash
# View application logs
doctl apps logs <app-id> --type=deploy
doctl apps logs <app-id> --type=build

# View runtime logs
doctl apps logs <app-id> --follow
```

## 🛠️ Troubleshooting

### Common Issues

#### Migration Fails
```bash
# Check SQLite database exists
ls -la backend/customs_portal.db

# Test PostgreSQL connection
psql "postgresql://user:pass@host:25060/db?sslmode=require"

# Run migration with verbose output
python migration/sqlite_to_postgres.py --verbose
```

#### App Won't Start
```bash
# Check build logs
doctl apps logs <app-id> --type=build

# Check environment variables
doctl apps get <app-id>

# Verify database connection
doctl databases get <db-id>
```

#### Frontend Can't Connect to Backend
- Verify CORS_ORIGINS includes frontend domain
- Check API_URL in frontend environment variables
- Ensure both services are deployed and healthy

## 📚 Additional Resources

- [Digital Ocean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [PostgreSQL Migration Guide](https://docs.digitalocean.com/products/databases/postgresql/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)

## 🆘 Support

### Getting Help
1. Check the troubleshooting section above
2. Review Digital Ocean documentation
3. Contact Digital Ocean support
4. Check GitHub issues for common problems

### Emergency Procedures
- **Rollback**: Use previous deployment in Digital Ocean dashboard
- **Database Recovery**: Restore from automated backups
- **Scale Up**: Increase instance sizes in app configuration

---

## 📋 Deployment Steps Summary

1. **Prepare**: Set up Digital Ocean account and GitHub repository
2. **Configure**: Set environment variables and secrets
3. **Database**: Create PostgreSQL and run migration
4. **Deploy**: Deploy application to App Platform
5. **Verify**: Test all functionality works correctly
6. **Monitor**: Set up monitoring and alerts

**Total deployment time: 15-30 minutes**

---

**Need help?** Check `DEPLOYMENT_CHECKLIST.md` for detailed step-by-step instructions.

# 🚀 Digital Ocean Deployment Checklist

## Pre-Deployment Setup

### 1. Digital Ocean Account Setup
- [ ] Create Digital Ocean account
- [ ] Add payment method
- [ ] Install doctl CLI tool
- [ ] Authenticate with Digital Ocean: `doctl auth init`

### 2. Repository Setup
- [ ] Create GitHub repository for the project
- [ ] Push all code to GitHub
- [ ] Ensure repository is public or add Digital Ocean as collaborator
- [ ] Verify all sensitive data is in environment variables, not code

### 3. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Generate secure `SECRET_KEY`: `openssl rand -base64 64`
- [ ] Generate secure `POSTGRES_PASSWORD`: `openssl rand -base64 32`
- [ ] Add Anthropic API key (if using AI features)
- [ ] Update CORS origins for production domain

### 4. Database Preparation
- [ ] Verify SQLite database exists: `backend/customs_portal.db`
- [ ] Test migration script locally
- [ ] Backup SQLite database
- [ ] Verify PostgreSQL schema is ready: `database/schema.sql`

## Deployment Process

### Phase 1: Database Setup
- [ ] Create managed PostgreSQL database on Digital Ocean
- [ ] Configure database firewall rules
- [ ] Test database connectivity
- [ ] Run schema creation: `psql -f database/schema.sql`
- [ ] Execute data migration: `python migration/sqlite_to_postgres.py`
- [ ] Validate migration results

### Phase 2: Application Deployment
- [ ] Update `deployment/app.yaml` with correct GitHub repository
- [ ] Deploy backend service to App Platform
- [ ] Deploy frontend service to App Platform
- [ ] Configure environment variables in Digital Ocean dashboard
- [ ] Set up health checks

### Phase 3: Configuration
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificates
- [ ] Configure CDN (optional)
- [ ] Set up monitoring and alerts

## Post-Deployment Verification

### 1. Backend API Testing
- [ ] Health check: `GET /health`
- [ ] API documentation: `GET /docs`
- [ ] Tariff sections: `GET /api/tariff/sections`
- [ ] Search functionality: `GET /api/search/tariff?q=test`
- [ ] Duty calculation: `POST /api/duty/calculate`

### 2. Frontend Testing
- [ ] Homepage loads correctly
- [ ] Navigation works between pages
- [ ] API calls succeed
- [ ] Search functionality works
- [ ] Responsive design on mobile

### 3. Database Verification
- [ ] All tables populated correctly
- [ ] Foreign key relationships intact
- [ ] Full-text search indexes working
- [ ] Performance acceptable

### 4. Security Verification
- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Rate limiting active
- [ ] No sensitive data exposed in logs
- [ ] Environment variables secure

## Monitoring Setup

### 1. Application Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure error alerting
- [ ] Monitor response times
- [ ] Track API usage

### 2. Database Monitoring
- [ ] Monitor connection pool usage
- [ ] Track query performance
- [ ] Set up backup verification
- [ ] Monitor disk usage

### 3. Cost Monitoring
- [ ] Set up billing alerts
- [ ] Monitor resource usage
- [ ] Optimize instance sizes
- [ ] Review monthly costs

## Maintenance Procedures

### 1. Regular Updates
- [ ] Update dependencies monthly
- [ ] Apply security patches
- [ ] Update database schema as needed
- [ ] Refresh SSL certificates

### 2. Backup Strategy
- [ ] Verify automated database backups
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Store backups securely

### 3. Performance Optimization
- [ ] Monitor and optimize slow queries
- [ ] Review and adjust connection pool settings
- [ ] Optimize frontend bundle size
- [ ] Configure CDN for static assets

## Troubleshooting Guide

### Common Issues

#### Database Connection Issues
```bash
# Check database status
doctl databases get customs-broker-portal-db

# Test connection
psql "postgresql://user:pass@host:25060/customs_broker_portal?sslmode=require"
```

#### Application Not Starting
```bash
# Check app logs
doctl apps logs <app-id> --type=build
doctl apps logs <app-id> --type=deploy

# Check environment variables
doctl apps get <app-id>
```

#### Migration Issues
```bash
# Re-run migration with verbose output
python migration/sqlite_to_postgres.py --verbose

# Check data integrity
python migration/validate_migration.py
```

### Performance Issues
- Check database connection pool settings
- Monitor query performance
- Review application logs for errors
- Verify CDN configuration

### Security Issues
- Rotate secrets regularly
- Monitor for unusual access patterns
- Keep dependencies updated
- Review CORS settings

## Emergency Procedures

### 1. Rollback Deployment
```bash
# Get previous deployment
doctl apps list-deployments <app-id>

# Rollback to previous version
doctl apps create-deployment <app-id> --spec=previous-spec.yaml
```

### 2. Database Recovery
```bash
# Restore from backup
doctl databases backups list customs-broker-portal-db
doctl databases backups restore <backup-id>
```

### 3. Emergency Contacts
- Digital Ocean Support: support.digitalocean.com
- Database Administrator: [contact info]
- Development Team: [contact info]

## Cost Optimization

### Current Estimated Costs
- App Platform (Professional): $12/month
- PostgreSQL (Basic): $15/month
- Total: ~$27/month

### Optimization Strategies
- Start with basic instances, scale up as needed
- Use managed services for reliability
- Monitor usage and adjust resources
- Consider reserved instances for long-term savings

## Success Metrics

### Technical Metrics
- Uptime: >99.5%
- Response time: <500ms for API calls
- Error rate: <1%
- Database query time: <100ms average

### Business Metrics
- User adoption rate
- Feature usage statistics
- Cost per user
- Customer satisfaction

---

## Quick Commands Reference

```bash
# Deploy application
./deployment/deploy.sh

# Check deployment status
doctl apps list

# View logs
doctl apps logs <app-id>

# Update environment variables
# (Done through Digital Ocean dashboard)

# Scale application
doctl apps update <app-id> --spec=updated-spec.yaml

# Database operations
doctl databases list
doctl databases get <db-id>
doctl databases backups list <db-id>
```

## Support Resources

- [Digital Ocean Documentation](https://docs.digitalocean.com/)
- [App Platform Guide](https://docs.digitalocean.com/products/app-platform/)
- [Managed Databases](https://docs.digitalocean.com/products/databases/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)

---

**Last Updated:** December 2024  
**Version:** 1.0  
**Status:** Production Ready ✅

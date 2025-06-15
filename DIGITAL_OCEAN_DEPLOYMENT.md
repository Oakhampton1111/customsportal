# 🚀 Digital Ocean Deployment Guide

## Quick Deployment Steps

### Method 1: Using App Spec File (Recommended)

1. **Go to Digital Ocean App Platform**
   - Visit: https://cloud.digitalocean.com/apps
   - Click "Create App"

2. **Choose "Import from App Spec"**
   - Select "Import from App Spec" option
   - Upload the `.do/app.yaml` file from this repository

3. **Configure Environment Variables**
   - Add these required secrets in the Digital Ocean dashboard:
   ```
   SECRET_KEY=your-generated-secret-key
   ANTHROPIC_API_KEY=your-anthropic-api-key (optional)
   ```

4. **Deploy**
   - Click "Create Resources"
   - Digital Ocean will automatically create the database and deploy both services

### Method 2: Using GitHub Integration

1. **Create App from GitHub**
   - Choose "GitHub" as source
   - Select repository: `Oakhampton1111/customsportal`
   - Branch: `master`

2. **Configure Services Manually**
   - **Backend Service:**
     - Source Directory: `/backend`
     - Build Command: (leave empty)
     - Run Command: `python main.py`
     - Environment: Python
     - Port: 8000

   - **Frontend Service:**
     - Source Directory: `/frontend`
     - Build Command: `npm run build`
     - Run Command: `npm run preview -- --host 0.0.0.0 --port $PORT`
     - Environment: Node.js
     - Port: 8080

3. **Add Database**
   - Add PostgreSQL database (Basic plan)
   - Name: `db`

4. **Configure Environment Variables**
   - Backend service needs:
     ```
     DATABASE_URL=${db.DATABASE_URL}
     SECRET_KEY=your-secret-key
     ENVIRONMENT=production
     CORS_ORIGINS=https://your-app-name.ondigitalocean.app
     ```
   - Frontend service needs:
     ```
     VITE_API_URL=https://your-app-name.ondigitalocean.app
     VITE_ENVIRONMENT=production
     ```

## 📋 App Spec Configuration

The `.do/app.yaml` file contains the complete configuration:

- **Backend**: Python/FastAPI service from `/backend` directory
- **Frontend**: Node.js/React service from `/frontend` directory  
- **Database**: PostgreSQL 15 managed database
- **Environment Variables**: Pre-configured with placeholders
- **Health Checks**: Automatic monitoring
- **Routing**: API routes to backend, all others to frontend

## 💰 Estimated Costs

- **App Platform (Basic)**: $5/month per service = $10/month
- **PostgreSQL (Basic)**: $15/month
- **Total**: ~$25/month

## 🔧 Post-Deployment

1. **Database Migration**
   - Run the migration script: `python migration/sqlite_to_postgres.py`
   - This transfers all 42,405+ records from SQLite to PostgreSQL

2. **Verify Deployment**
   - Frontend: `https://your-app-name.ondigitalocean.app`
   - API Health: `https://your-app-name.ondigitalocean.app/health`
   - API Docs: `https://your-app-name.ondigitalocean.app/docs`

3. **Monitor Performance**
   - Check Digital Ocean dashboard for metrics
   - Monitor database performance
   - Review application logs

## 🛠️ Troubleshooting

### Build Issues
- Check build logs in Digital Ocean dashboard
- Verify source directories are correct
- Ensure environment variables are set

### Database Connection Issues
- Verify DATABASE_URL is automatically injected
- Check database firewall settings
- Test connection from backend service

### Frontend/Backend Communication
- Verify CORS_ORIGINS includes frontend domain
- Check VITE_API_URL points to correct backend
- Ensure both services are deployed and healthy

## 📚 Additional Resources

- [Digital Ocean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [App Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)
- [PostgreSQL Migration Guide](migration/sqlite_to_postgres.py)

---

**Repository**: https://github.com/Oakhampton1111/customsportal.git  
**App Spec**: `.do/app.yaml`  
**Status**: ✅ Ready for Deployment

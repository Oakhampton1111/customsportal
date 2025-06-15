# 🚀 Simple Digital Ocean Deployment

## Quick Deploy Steps

### Option 1: App Spec Upload (Recommended)

1. **Download App Spec**
   - Download `.do/app.yaml` from this repository
   - Save it to your computer

2. **Create App**
   - Go to: https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Choose "Import from App Spec"
   - Upload the `.do/app.yaml` file

3. **Add Secrets**
   - In Digital Ocean dashboard, add these environment variables:
   ```
   SECRET_KEY=your-secret-key-here
   ANTHROPIC_API_KEY=your-api-key-here
   ```
   - Generate SECRET_KEY: `openssl rand -base64 64`

4. **Deploy**
   - Click "Create Resources"
   - Wait for deployment to complete

### Option 2: GitHub Integration

1. **Connect Repository**
   - Choose "GitHub" as source
   - Select: `Oakhampton1111/customsportal`
   - Branch: `master`

2. **Configure Services**
   - **Backend Service:**
     - Name: `backend`
     - Source Directory: `/backend`
     - Build Method: `Dockerfile`
     - Dockerfile Path: `backend/Dockerfile`
     - Port: `8000`
     - Health Check: `/health`

   - **Frontend Service:**
     - Name: `frontend`
     - Source Directory: `/frontend`
     - Build Method: `Dockerfile`
     - Dockerfile Path: `frontend/Dockerfile`
     - Port: `8080`

3. **Add Database**
   - Add PostgreSQL database
   - Plan: Basic ($15/month)
   - Name: `db`

4. **Environment Variables**
   - Backend:
     ```
     DATABASE_URL=${db.DATABASE_URL}
     SECRET_KEY=your-secret-key
     ENVIRONMENT=production
     CORS_ORIGINS=https://your-app-name.ondigitalocean.app
     ```
   - Frontend:
     ```
     VITE_API_URL=https://your-app-name.ondigitalocean.app
     VITE_ENVIRONMENT=production
     ```

## After Deployment

1. **Test Endpoints**
   - Frontend: `https://your-app.ondigitalocean.app`
   - API Health: `https://your-app.ondigitalocean.app/health`
   - API Docs: `https://your-app.ondigitalocean.app/docs`

2. **Run Database Migration**
   ```bash
   python migration/sqlite_to_postgres.py
   ```

## Cost: ~$25/month
- App Platform: $10/month (2 services)
- PostgreSQL: $15/month

## Repository
https://github.com/Oakhampton1111/customsportal.git

## Files Ready
- ✅ Docker containers for both services
- ✅ App Platform configuration
- ✅ Database migration script
- ✅ Production environment setup

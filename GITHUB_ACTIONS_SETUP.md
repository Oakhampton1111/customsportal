# 🚀 GitHub Actions Auto-Deployment Setup

## Overview
This solution uses GitHub Actions to automatically deploy to Digital Ocean on every push to the master branch, bypassing the need to configure auto-deployment in Digital Ocean itself.

## ✅ What This Does
- **Triggers on every push** to master branch
- **Uses Digital Ocean CLI** to force rebuild and deploy
- **Monitors deployment progress** and waits for completion
- **Verifies deployment** by testing health endpoint
- **Provides clear feedback** on success or failure

## 🔧 Setup Instructions

### Step 1: Create Digital Ocean API Token
1. Go to [Digital Ocean API Tokens](https://cloud.digitalocean.com/account/api/tokens)
2. Click **Generate New Token**
3. Name: `GitHub Actions Deployment`
4. Scopes: **Full Access** (or at minimum: `read` and `write` for Apps)
5. Click **Generate Token**
6. **Copy the token** (you won't see it again!)

### Step 2: Add Token to GitHub Secrets
1. Go to your GitHub repository: `https://github.com/Oakhampton1111/customsportal`
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `DIGITALOCEAN_ACCESS_TOKEN`
6. Value: Paste the token from Step 1
7. Click **Add secret**

### Step 3: Verify Workflow File
The workflow file is already created at `.github/workflows/deploy-to-digital-ocean.yml`

Key features:
- ✅ Triggers on push to master
- ✅ Uses official Digital Ocean GitHub Action
- ✅ Automatically finds your app by name
- ✅ Forces rebuild to ensure latest code
- ✅ Waits for deployment completion
- ✅ Verifies health endpoint

### Step 4: Test the Workflow
```bash
# Commit all your health check fixes
git add .
git commit -m "Fix: Add GitHub Actions auto-deployment

- Resolve Digital Ocean health check failures
- Add GitHub Actions workflow for auto-deployment
- Fix backend health check localhost binding
- Add curl to frontend container
- Improve database connection retry logic"

# Push to trigger the workflow
git push origin master
```

### Step 5: Monitor the Deployment
1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see "Deploy to Digital Ocean" workflow running
4. Click on the workflow run to see detailed logs
5. Watch for successful completion and health check verification

## 📊 Workflow Stages

### Stage 1: Setup (30 seconds)
- ✅ Checkout code
- ✅ Install Digital Ocean CLI
- ✅ Authenticate with API token

### Stage 2: Deploy (8-12 minutes)
- ✅ Find your app ID automatically
- ✅ Trigger force rebuild deployment
- ✅ Monitor deployment progress
- ✅ Wait for "ACTIVE" status

### Stage 3: Verify (1-2 minutes)
- ✅ Test health endpoint
- ✅ Confirm deployment success
- ✅ Provide feedback

## 🔍 Monitoring and Logs

### GitHub Actions Logs
- **Real-time progress**: See each step as it executes
- **Deployment status**: Monitor Digital Ocean deployment progress
- **Health check results**: Verify your app is responding
- **Error details**: Clear error messages if something fails

### Expected Log Output
```
✅ Found App ID: abc123def456
✅ Triggering deployment for app ID: abc123def456
✅ Deployment status: PENDING_BUILD
✅ Deployment status: BUILDING
✅ Deployment status: DEPLOYING
✅ Deployment completed successfully!
✅ Deployment verification successful!
🎉 Deployment to Digital Ocean completed successfully!
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "DIGITALOCEAN_ACCESS_TOKEN not found"
- **Solution**: Ensure you added the secret in GitHub repository settings
- **Check**: Settings → Secrets and variables → Actions

#### 2. "App not found"
- **Solution**: Verify your app name is exactly "customs-broker-portal"
- **Check**: Digital Ocean dashboard app name

#### 3. "Deployment failed"
- **Solution**: Check the specific error in GitHub Actions logs
- **Common causes**: Build errors, health check failures, resource limits

#### 4. "Health check failed"
- **Solution**: The health check fixes should resolve this
- **Verify**: Check that your health endpoint improvements are included

### Manual Verification
If the workflow completes but you want to double-check:

```bash
# Test health endpoint manually
curl https://customs-broker-portal.ondigitalocean.app/health

# Expected response:
{
  "status": "healthy",
  "system": { ... },
  "database": {
    "status": "healthy",
    "connection_test": true
  }
}
```

## 🎯 Benefits of This Approach

### Advantages:
- ✅ **No Digital Ocean configuration needed**: Bypasses app spec issues
- ✅ **Full control**: You can customize the deployment process
- ✅ **Detailed logging**: See exactly what's happening
- ✅ **Automatic verification**: Tests health endpoint after deployment
- ✅ **Force rebuild**: Ensures latest code is always deployed

### Workflow Features:
- 🔄 **Automatic trigger**: Every push to master deploys
- ⏱️ **Timeout protection**: Won't hang indefinitely
- 🔍 **Status monitoring**: Tracks deployment progress
- ✅ **Health verification**: Confirms app is working
- 📊 **Clear feedback**: Success/failure notifications

## 🔄 Future Customizations

### Add Slack Notifications
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Add Database Migration
```yaml
- name: Run Database Migration
  run: |
    # Add migration commands here
    echo "Running database migrations..."
```

### Add Testing Before Deploy
```yaml
- name: Run Tests
  run: |
    # Add test commands here
    python -m pytest backend/tests/
```

## 📋 Quick Reference

### Repository Secrets Needed:
- `DIGITALOCEAN_ACCESS_TOKEN`: Your Digital Ocean API token

### Workflow Triggers:
- Push to `master` branch
- Pull request to `master` branch (for testing)

### Deployment URL:
- **App**: https://customs-broker-portal.ondigitalocean.app
- **Health**: https://customs-broker-portal.ondigitalocean.app/health
- **API Docs**: https://customs-broker-portal.ondigitalocean.app/docs

---

## 🚀 Ready to Deploy!

Once you've added the `DIGITALOCEAN_ACCESS_TOKEN` secret to GitHub, simply push your code:

```bash
git push origin master
```

The GitHub Actions workflow will automatically:
1. Deploy your health check fixes
2. Ensure the deployment succeeds
3. Verify the app is healthy
4. Provide clear success/failure feedback

**This approach is much more reliable than trying to configure auto-deployment in Digital Ocean!** 🎉

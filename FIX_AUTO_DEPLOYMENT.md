# 🔧 Fix Auto-Deployment Issue - Step by Step

## Problem Identified
Your Digital Ocean app exists but is missing the `deploy_on_push: true` configuration in both services. This is why it's not auto-deploying when you push to GitHub.

## 🎯 Solution: Update App Spec in Digital Ocean

### Step 1: Access Your App Settings
1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Click on your app: **customs-broker-portal**
3. Click the **Settings** tab
4. Scroll down to **App Spec** section
5. Click **Edit**

### Step 2: Update the App Spec
1. In the App Spec editor, you'll see your current configuration
2. **Download** the current spec as backup (click Download button)
3. **Replace the entire content** with the corrected spec from `digital_ocean_app_spec.yaml`

### Step 3: Key Changes Made
The corrected spec includes:

#### Backend Service Changes:
```yaml
git:
  branch: master
  repo_clone_url: https://github.com/Oakhampton1111/customsportal.git
  deploy_on_push: true  # ← ADDED THIS
health_check:
  http_path: /health
  initial_delay_seconds: 60  # ← ADDED THIS
  period_seconds: 30         # ← ADDED THIS
  timeout_seconds: 10        # ← ADDED THIS
  failure_threshold: 5       # ← ADDED THIS
envs:
  # ... existing environment variables ...
  - key: HOST                # ← ADDED THIS
    scope: RUN_AND_BUILD_TIME
    value: "0.0.0.0"
  - key: PORT                # ← ADDED THIS
    scope: RUN_AND_BUILD_TIME
    value: "8000"
```

#### Frontend Service Changes:
```yaml
git:
  branch: master
  repo_clone_url: https://github.com/Oakhampton1111/customsportal.git
  deploy_on_push: true  # ← ADDED THIS
```

### Step 4: Apply the Changes
1. **Copy** the entire content from `digital_ocean_app_spec.yaml`
2. **Paste** it into the Digital Ocean App Spec editor
3. Click **Save** 
4. Digital Ocean will validate the spec
5. Click **Deploy** to apply the changes

### Step 5: Verify Auto-Deployment Setup
After the deployment completes:

1. **Check Service Configuration**:
   - Backend service should show "Auto-deploy: Enabled"
   - Frontend service should show "Auto-deploy: Enabled"

2. **Test Auto-Deployment**:
   ```bash
   # Make a small change to test
   echo "# Test auto-deployment" >> README.md
   git add README.md
   git commit -m "Test: Verify auto-deployment works"
   git push origin master
   ```

3. **Monitor Deployment**:
   - Go to **Activity** tab in Digital Ocean
   - You should see a new deployment triggered automatically
   - Watch for "Deployment started" notification

## 🚨 Important Notes

### Before Updating App Spec:
- ✅ **Backup Current Spec**: Download your current app spec before making changes
- ✅ **Verify Repository Access**: Ensure Digital Ocean has access to your GitHub repo
- ✅ **Check Branch Name**: Confirm you're using `master` branch (not `main`)

### After Updating App Spec:
- ⏱️ **Initial Deployment**: The first deployment after updating spec may take 10-15 minutes
- 🔍 **Monitor Health Checks**: Watch for health check improvements with new timing
- 📊 **Verify Auto-Deploy**: Test with a small commit to confirm auto-deployment works

## 🔍 Troubleshooting

### If App Spec Update Fails:
1. **Validation Errors**: Check YAML syntax and indentation
2. **Permission Issues**: Verify GitHub repository access
3. **Resource Conflicts**: Ensure database names match existing resources

### If Auto-Deployment Still Doesn't Work:
1. **Check GitHub Webhooks**:
   - Go to your GitHub repo → Settings → Webhooks
   - Look for Digital Ocean webhook
   - Verify it's active and receiving events

2. **Verify Repository Settings**:
   - Ensure repository is public or Digital Ocean has access
   - Check that the branch name matches exactly (`master`)

3. **Test Manual Deployment**:
   - Try manual deployment first: App Platform → Actions → Force Rebuild
   - If manual works but auto doesn't, it's a webhook issue

## 📋 Expected Results After Fix

### Immediate Results:
- ✅ App spec updated successfully
- ✅ Services show "Auto-deploy: Enabled"
- ✅ Health checks configured with proper timing
- ✅ New environment variables applied

### After Next Git Push:
- ✅ Automatic deployment triggered
- ✅ Build process starts within 30 seconds
- ✅ Health checks pass with improved timing
- ✅ Services marked as "Healthy"

## 🎯 Success Verification

Run this command after updating the app spec and pushing code:

```bash
# Check if auto-deployment worked
curl https://customs-broker-portal.ondigitalocean.app/health

# Expected response:
{
  "status": "healthy",
  "system": { ... },
  "database": {
    "status": "healthy" or "initializing",
    "connection_test": true
  }
}
```

## 📞 Need Help?

If you encounter issues:
1. **Check Digital Ocean Activity Tab**: Look for error messages
2. **Review Build Logs**: Check for specific error details
3. **Verify GitHub Integration**: Ensure webhooks are working
4. **Test Manual Deployment**: Confirm code changes work manually first

---

**Next Step**: Update your app spec in Digital Ocean using the corrected `digital_ocean_app_spec.yaml` file! 🚀

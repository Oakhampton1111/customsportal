# 🤖 Claude Auto-Fix Setup Guide - Customs Broker Portal

## 📋 Overview
This guide provides complete setup instructions for the Claude Auto-Fix system specifically configured for the Customs Broker Portal. The system provides automated code fixing while preserving critical customs compliance, trade regulations, and business logic.

## 🎯 What's Included

### **GitHub Workflows**
- **Main CI/CD Pipeline** (`ci-cd.yml`) - Multi-stage quality gates with comprehensive testing
- **Claude Auto-Fix System** (`claude-auto-fix.yml`) - Automatic issue creation and Claude integration
- **Claude Code Action** (`claude.yml`) - AI-powered code analysis and PR creation

### **Business Context System**
- **Master Configuration** (`claude-config.yml`) - Centralized settings for customs domain
- **Business Rules** (`claude-business-rules.md`) - Customs compliance and trade logic
- **Critical Constraints** (`claude-constraints.md`) - "DO NOT TOUCH" areas for customs
- **UX Guidelines** (`claude-ux-context.md`) - User experience requirements
- **API Contracts** (`claude-api-contracts.md`) - Service specifications and data models

## 🚀 Quick Setup (5 Minutes)

### **Step 1: GitHub Secrets Configuration**
Go to: **Repository → Settings → Secrets and variables → Actions**

Add these required secrets:

#### **BOT_PAT** - GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token" → "Fine-grained tokens"
3. Select your repository
4. Grant these permissions:
   - **Repository permissions:**
     - Contents: Read and write
     - Issues: Write
     - Pull requests: Write
     - Metadata: Read
5. Copy the token and add it as `BOT_PAT` secret

#### **CLAUDE_API_KEY** - Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it as `CLAUDE_API_KEY` secret

#### **DOCKER_USERNAME** - Docker Hub Username
1. Create account at [Docker Hub](https://hub.docker.com/)
2. Add your Docker Hub username as `DOCKER_USERNAME` secret

#### **DOCKER_PASSWORD** - Docker Hub Access Token
1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Give it a name (e.g., "GitHub Actions")
4. Copy the token and add it as `DOCKER_PASSWORD` secret

#### **DIGITALOCEAN_ACCESS_TOKEN** - Digital Ocean API Token
1. Go to [Digital Ocean Control Panel](https://cloud.digitalocean.com/)
2. Navigate to API → Tokens/Keys
3. Click "Generate New Token"
4. Give it a name and select "Write" scope
5. Copy the token and add it as `DIGITALOCEAN_ACCESS_TOKEN` secret

### **Step 2: Verify Project Structure**
Ensure your project has the correct structure:
```
Customs Broker Portal/
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
├── backend/
│   ├── requirements.txt
│   └── *.py files
└── .github/
    ├── workflows/
    │   ├── ci-cd.yml
    │   ├── claude-auto-fix.yml
    │   └── claude.yml
    ├── claude-config.yml
    ├── claude-business-rules.md
    ├── claude-constraints.md
    ├── claude-ux-context.md
    └── claude-api-contracts.md
```

### **Step 3: Test the System**
1. **Commit and push** all the new files to your repository
2. **Create a test branch** with intentional TypeScript errors:
   ```bash
   git checkout -b test-claude-autofix
   # Add some TypeScript errors to frontend files
   git commit -am "Test: Add TypeScript errors for Claude"
   git push origin test-claude-autofix
   ```
3. **Verify the pipeline fails** and creates an auto-fix issue
4. **Check that Claude responds** and creates a fix PR

## 🔧 How It Works

### **Automated Workflow**
1. **Code Push** → CI pipeline runs with 4 quality gates
2. **CI Fails** → Auto-fix workflow creates detailed issue
3. **PAT Comment** triggers Claude with customs business context
4. **Claude Analyzes** failures using your customs documentation
5. **Claude Creates PR** with targeted fixes
6. **CI Re-runs** and iterates until all quality gates pass
7. **System Deploys** once everything is green

### **Quality Gates for Customs Portal**
1. **Frontend TypeScript & Linting** - React/TypeScript compilation and ESLint
2. **Backend Code Quality & Tests** - Python formatting, type checking, and pytest
3. **Frontend Unit Tests** - Jest and React Testing Library
4. **End-to-End Tests** - Playwright browser testing

## 🏢 Customs-Specific Configuration

### **Ultra-Conservative Approach**
The system is configured with an ultra-conservative approach for customs compliance:
- **Minimal changes only** - Focus on syntax fixes, avoid refactoring
- **Preserve calculations** - Never modify duty or tax calculations
- **Maintain compliance** - Keep all regulatory validation intact
- **Audit trail protection** - Preserve complete activity logging

### **Protected Areas**
Claude will **NEVER** modify:
- Tariff classification algorithms
- Duty calculation formulas
- Trade agreement rules
- Compliance validation logic
- Multi-tenant data isolation
- Audit trail systems

## 📊 Business Context Priority

The system prioritizes business context in this order:
1. **Critical Constraints** - Absolute "DO NOT TOUCH" areas
2. **Business Rules** - Customs compliance and trade logic
3. **API Contracts** - Service compatibility
4. **UX Guidelines** - User experience requirements
5. **Master Configuration** - System settings

## 🔍 Monitoring & Success Metrics

### **System Health Indicators**
- **Fix Success Rate**: Target > 80%
- **CI Pipeline Time**: Target < 10 minutes
- **Claude Response Time**: Target < 2 minutes
- **False Positive Rate**: Target < 10%

### **Quality Metrics**
- **TypeScript Errors**: 0
- **Linting Warnings**: 0
- **Test Coverage**: > 80%
- **Security Vulnerabilities**: 0

## 🚨 Troubleshooting

### **Common Issues**

#### **"Bad credentials" Error**
- Check that `BOT_PAT` secret is correctly set
- Verify PAT token has required permissions
- Ensure token hasn't expired

#### **Claude Doesn't Respond**
- Verify `CLAUDE_API_KEY` secret is set
- Check that Claude workflow has proper permissions
- Ensure `@claude` mention is in issue comment

#### **CI Pipeline Fails**
- Update commands in `ci-cd.yml` to match your project
- Check working directories are correct
- Verify dependencies are properly installed

#### **Permission Errors**
- Ensure workflow has `contents: write` permission
- Check that PAT token has repository access
- Verify user has admin access to repository

## 🎯 Customization Options

### **Adjusting Quality Gates**
Edit `.github/workflows/ci-cd.yml` to modify commands:
```yaml
# Example: Change test command
- name: 🧪 Run Unit Tests
  working-directory: frontend
  run: npm run test:ci  # Change to your test command
```

### **Adding Custom Rules**
Edit `.github/claude-config.yml` to add project-specific rules:
```yaml
custom_rules:
  - name: "Preserve legacy customs API"
    description: "Don't modify legacy customs endpoints"
    pattern: "legacy_customs|old_api"
    action: "preserve"
```

### **Modifying Business Context**
Update the business context files to match your specific requirements:
- **claude-business-rules.md** - Add your specific customs workflows
- **claude-constraints.md** - Add your "DO NOT TOUCH" areas
- **claude-ux-context.md** - Customize for your UI patterns
- **claude-api-contracts.md** - Update with your API specifications

## 📝 Best Practices

### **For Customs Compliance**
- **Document everything** - Keep business context files updated
- **Test thoroughly** - Verify customs calculations after any changes
- **Review PRs carefully** - Human review is still essential for customs
- **Monitor success rates** - Track how often Claude fixes work
- **Update regularly** - Keep business rules current with regulations

### **For System Maintenance**
- **Rotate secrets** - Regularly update API keys and tokens
- **Monitor logs** - Check GitHub Actions logs for issues
- **Update dependencies** - Keep Claude action version current
- **Backup configurations** - Version control all configuration files

## 🔐 Security Considerations

### **Secrets Management**
- **Minimal permissions** - Grant only necessary access to PAT token
- **Regular rotation** - Update API keys and tokens periodically
- **Audit access** - Monitor who has access to secrets
- **Secure storage** - Use GitHub secrets, never commit keys to code

### **Customs Data Protection**
- **Client isolation** - Ensure multi-tenant data separation
- **Audit trails** - Maintain complete activity logging
- **Compliance monitoring** - Track all customs-related changes
- **Data encryption** - Protect sensitive trade information

## 📞 Support & Help

### **Getting Help**
1. **Check logs** - GitHub Actions → Workflow runs
2. **Review documentation** - Read the business context files
3. **Test locally** - Run CI commands on your machine
4. **Validate configuration** - Check YAML syntax and paths

### **Escalation Process**
For customs-specific issues:
1. **Create detailed issue** - Document the customs compliance concern
2. **Flag for expert review** - Require customs domain specialist
3. **Preserve existing logic** - Keep current implementation intact
4. **Manual intervention** - Human customs expert review

## 🎉 Success!

Your Claude Auto-Fix system is now configured for the Customs Broker Portal with:
- ✅ Automated code fixing with customs compliance awareness
- ✅ Multi-stage quality gates for comprehensive testing
- ✅ Business context preservation for trade regulations
- ✅ Ultra-conservative approach for regulatory safety
- ✅ Complete audit trail and monitoring

The system will now automatically detect CI failures and create Claude-powered fixes while preserving your critical customs business logic and compliance requirements.

## 🔗 Additional Resources

- [Claude Code Action Documentation](https://github.com/anthropics/claude-code-action)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Customs Compliance Best Practices](./claude-business-rules.md)
- [System Constraints Reference](./claude-constraints.md)

---

**Remember**: This system is designed to be ultra-conservative for customs compliance. It's better to leave broken syntax than to break customs regulations or financial calculations.
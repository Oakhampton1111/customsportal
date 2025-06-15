#!/bin/bash

# Customs Broker Portal - Digital Ocean Deployment Script
# This script automates the deployment process to Digital Ocean

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="customs-broker-portal"
POSTGRES_PASSWORD=""
SECRET_KEY=""
ANTHROPIC_API_KEY=""

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        print_error "doctl CLI is not installed. Please install it first:"
        echo "  curl -sL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz | tar -xzv"
        echo "  sudo mv doctl /usr/local/bin"
        exit 1
    fi
    
    # Check if authenticated
    if ! doctl account get &> /dev/null; then
        print_error "Not authenticated with Digital Ocean. Please run:"
        echo "  doctl auth init"
        exit 1
    fi
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        print_error "Not in a git repository. Please initialize git first:"
        echo "  git init"
        echo "  git add ."
        echo "  git commit -m 'Initial commit'"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Collect configuration
collect_config() {
    print_header "Configuration Setup"
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        print_info "Found .env file, loading configuration..."
        source .env
        POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-""}
        SECRET_KEY=${SECRET_KEY:-""}
        ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-""}
    fi
    
    # Prompt for missing values
    if [ -z "$POSTGRES_PASSWORD" ]; then
        echo -n "Enter PostgreSQL password (will be generated if empty): "
        read -s POSTGRES_PASSWORD
        echo
        if [ -z "$POSTGRES_PASSWORD" ]; then
            POSTGRES_PASSWORD=$(openssl rand -base64 32)
            print_info "Generated PostgreSQL password"
        fi
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        echo -n "Enter secret key (will be generated if empty): "
        read -s SECRET_KEY
        echo
        if [ -z "$SECRET_KEY" ]; then
            SECRET_KEY=$(openssl rand -base64 64)
            print_info "Generated secret key"
        fi
    fi
    
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -n "Enter Anthropic API key (optional): "
        read -s ANTHROPIC_API_KEY
        echo
    fi
    
    print_success "Configuration collected"
}

# Create PostgreSQL database
create_database() {
    print_header "Creating PostgreSQL Database"
    
    # Check if database already exists
    DB_EXISTS=$(doctl databases list --format Name --no-header | grep -c "^${PROJECT_NAME}-db$" || true)
    
    if [ "$DB_EXISTS" -eq 0 ]; then
        print_info "Creating PostgreSQL database..."
        doctl databases create ${PROJECT_NAME}-db \
            --engine pg \
            --version 15 \
            --size db-s-1vcpu-1gb \
            --region nyc3
        
        print_info "Waiting for database to be ready..."
        while true; do
            STATUS=$(doctl databases get ${PROJECT_NAME}-db --format Status --no-header)
            if [ "$STATUS" = "online" ]; then
                break
            fi
            echo -n "."
            sleep 10
        done
        echo
        
        print_success "Database created successfully"
    else
        print_warning "Database already exists"
    fi
    
    # Get database connection details
    DB_CONNECTION=$(doctl databases connection ${PROJECT_NAME}-db --format URI --no-header)
    print_info "Database connection: ${DB_CONNECTION}"
}

# Run database migration
run_migration() {
    print_header "Running Database Migration"
    
    if [ ! -f "backend/customs_portal.db" ]; then
        print_warning "SQLite database not found, skipping migration"
        return
    fi
    
    print_info "Installing migration dependencies..."
    pip install asyncpg
    
    print_info "Running migration script..."
    cd migration
    python sqlite_to_postgres.py "../backend/customs_portal.db" "$DB_CONNECTION"
    cd ..
    
    print_success "Database migration completed"
}

# Deploy to App Platform
deploy_app() {
    print_header "Deploying to App Platform"
    
    # Update app.yaml with actual repository
    REPO_URL=$(git config --get remote.origin.url)
    if [ -z "$REPO_URL" ]; then
        print_error "No git remote origin found. Please add your repository:"
        echo "  git remote add origin https://github.com/username/customs-broker-portal.git"
        exit 1
    fi
    
    # Extract repo name from URL
    REPO_NAME=$(echo $REPO_URL | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
    
    # Create temporary app spec
    cp deployment/app.yaml deployment/app-deploy.yaml
    sed -i "s/your-username\/customs-broker-portal/$REPO_NAME/g" deployment/app-deploy.yaml
    
    # Check if app already exists
    APP_EXISTS=$(doctl apps list --format Name --no-header | grep -c "^${PROJECT_NAME}$" || true)
    
    if [ "$APP_EXISTS" -eq 0 ]; then
        print_info "Creating new app..."
        doctl apps create deployment/app-deploy.yaml
    else
        print_info "Updating existing app..."
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "${PROJECT_NAME}$" | awk '{print $1}')
        doctl apps update $APP_ID deployment/app-deploy.yaml
    fi
    
    # Clean up temporary file
    rm deployment/app-deploy.yaml
    
    print_success "App deployment initiated"
}

# Set environment variables
set_env_vars() {
    print_header "Setting Environment Variables"
    
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "${PROJECT_NAME}$" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        print_error "App not found"
        exit 1
    fi
    
    print_info "Setting secrets..."
    
    # Note: doctl doesn't have direct env var setting, so we'll provide instructions
    print_warning "Please set the following environment variables in the Digital Ocean dashboard:"
    echo "  App Platform > ${PROJECT_NAME} > Settings > Environment Variables"
    echo ""
    echo "  SECRET_KEY (encrypted): ${SECRET_KEY}"
    echo "  ANTHROPIC_API_KEY (encrypted): ${ANTHROPIC_API_KEY}"
    echo ""
    echo "  Database URL will be automatically set by the managed database."
}

# Monitor deployment
monitor_deployment() {
    print_header "Monitoring Deployment"
    
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "${PROJECT_NAME}$" | awk '{print $1}')
    
    print_info "Deployment status:"
    doctl apps get $APP_ID
    
    print_info "Live URL will be available at:"
    echo "  https://${PROJECT_NAME}.ondigitalocean.app"
    
    print_info "To monitor logs:"
    echo "  doctl apps logs $APP_ID --type=build"
    echo "  doctl apps logs $APP_ID --type=deploy"
}

# Main deployment flow
main() {
    print_header "🏛️  Customs Broker Portal - Digital Ocean Deployment"
    
    check_prerequisites
    collect_config
    create_database
    run_migration
    deploy_app
    set_env_vars
    monitor_deployment
    
    print_header "🎉 Deployment Complete!"
    print_success "Your Customs Broker Portal is being deployed to Digital Ocean"
    print_info "It may take 5-10 minutes for the deployment to complete"
    print_info "Check the Digital Ocean dashboard for deployment status"
}

# Run main function
main "$@"

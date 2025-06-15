#!/usr/bin/env python3
"""
Startup script for the Customs Broker Portal FastAPI backend.

This script provides a convenient way to start the application with
proper error handling and environment validation.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from main import main
    from config import get_settings, is_development
    from database import test_database_connection, init_database
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you have installed all dependencies with: pip install -r requirements.txt")
    sys.exit(1)


async def validate_environment():
    """Validate the environment before starting the server."""
    settings = get_settings()
    
    print("Validating environment...")
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists() and is_development():
        print("Warning: .env file not found. Using default settings.")
        print("Copy .env.example to .env and configure your settings.")
    
    # Test database connection
    print("Testing database connection...")
    try:
        # Initialize database first
        await init_database()
        
        connection_ok = await test_database_connection()
        if connection_ok:
            print("Database connection successful")
        else:
            print("Database connection failed")
            print(f"Database URL: {settings.database_url}")
            print("Please check your database configuration.")
            return False
    except Exception as e:
        print(f"Database connection error: {e}")
        print("Make sure the database is accessible.")
        return False
    
    # Check required environment variables for production
    if not is_development():
        required_vars = ["SECRET_KEY", "DATABASE_URL"]
        missing_vars = []
        
        for var in required_vars:
            if not getattr(settings, var.lower(), None):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
    
    print("Environment validation passed")
    return True


def print_startup_info():
    """Print startup information."""
    settings = get_settings()
    
    print("\n" + "="*60)
    print("Customs Broker Portal API")
    print("="*60)
    print(f"Version: {settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print(f"Debug: {settings.debug}")
    print(f"Reload: {settings.reload}")
    
    if is_development():
        print(f"\nAPI Documentation:")
        print(f"Swagger UI: http://{settings.host}:{settings.port}{settings.docs_url}")
        print(f"ReDoc: http://{settings.host}:{settings.port}{settings.redoc_url}")
    
    print(f"\nHealth Check: http://{settings.host}:{settings.port}/health")
    print("="*60)


async def startup_checks():
    """Perform startup checks before launching the server."""
    print("Performing startup checks...")
    
    # Validate environment
    if not await validate_environment():
        print("\nStartup checks failed. Please fix the issues above.")
        sys.exit(1)
    
    print("All startup checks passed")


if __name__ == "__main__":
    try:
        # Print startup information
        print_startup_info()
        
        # Run startup checks
        asyncio.run(startup_checks())
        
        # Start the server
        print("\nStarting server...")
        main()
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFailed to start server: {e}")
        sys.exit(1)
/**
 * Global setup for integration tests - starts backend server and database
 */

import { spawn, ChildProcess } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';

let backendProcess: ChildProcess | null = null;
const dbProcess: ChildProcess | null = null;

const BACKEND_PORT = 8001; // Use different port for testing
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;
const MAX_STARTUP_TIME = 60000; // 60 seconds
const HEALTH_CHECK_INTERVAL = 1000; // 1 second

/**
 * Wait for a service to be ready by checking health endpoint
 */
async function waitForService(url: string, timeout: number = MAX_STARTUP_TIME): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    try {
      const response = await fetch(`${url}/health`);
      if (response.ok) {
        console.log(`✓ Service at ${url} is ready`);
        return;
      }
    } catch {
      // Service not ready yet, continue waiting
    }
    
    await new Promise(resolve => setTimeout(resolve, HEALTH_CHECK_INTERVAL));
  }
  
  throw new Error(`Service at ${url} failed to start within ${timeout}ms`);
}

/**
 * Start PostgreSQL database for testing
 */
async function startTestDatabase(): Promise<void> {
  console.log('🗄️  Starting test database...');
  
  // Check if PostgreSQL is available
  try {
    const psqlCheck = spawn('psql', ['--version'], { stdio: 'pipe' });
    
    await new Promise((resolve, reject) => {
      psqlCheck.on('close', (code: number) => {
        if (code === 0) {
          resolve(void 0);
        } else {
          reject(new Error('PostgreSQL not found. Please install PostgreSQL.'));
        }
      });
    });
  } catch {
    throw new Error('PostgreSQL not available. Please install and configure PostgreSQL.');
  }
  
  // Create test database if it doesn't exist
  const createDbProcess = spawn('createdb', ['customs_broker_portal_test'], {
    stdio: 'pipe',
    env: {
      ...process.env,
      PGUSER: process.env.PGUSER || 'postgres',
      PGPASSWORD: process.env.PGPASSWORD || 'password',
      PGHOST: process.env.PGHOST || 'localhost',
      PGPORT: process.env.PGPORT || '5432',
    }
  });
  
  await new Promise((resolve) => {
    createDbProcess.on('close', () => {
      // Database creation may fail if it already exists, which is fine
      resolve(void 0);
    });
  });
  
  console.log('✓ Test database ready');
}

/**
 * Start backend server for integration testing
 */
async function startBackendServer(): Promise<void> {
  console.log('🚀 Starting backend server for integration tests...');
  
  const backendDir = path.resolve(process.cwd(), '..', 'backend');
  
  // Check if backend directory exists
  try {
    await fs.access(backendDir);
  } catch {
    throw new Error(`Backend directory not found at ${backendDir}`);
  }
  
  // Set environment variables for testing
  const testEnv = {
    ...process.env,
    ENVIRONMENT: 'test',
    PORT: BACKEND_PORT.toString(),
    DATABASE_URL: 'postgresql+asyncpg://postgres:password@localhost:5432/customs_broker_portal_test',
    DEBUG: 'true',
    LOG_LEVEL: 'INFO',
    CORS_ORIGINS: 'http://localhost:3000,http://localhost:3001',
    SECRET_KEY: 'test-secret-key-for-integration-tests',
  };
  
  // Start backend server
  backendProcess = spawn('python', ['-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', BACKEND_PORT.toString()], {
    cwd: backendDir,
    env: testEnv,
    stdio: 'pipe',
  });
  
  if (!backendProcess) {
    throw new Error('Failed to start backend process');
  }
  
  // Handle backend process output
  backendProcess.stdout?.on('data', (data) => {
    const output = data.toString();
    if (output.includes('error') || output.includes('Error')) {
      console.error('Backend error:', output);
    }
  });
  
  backendProcess.stderr?.on('data', (data) => {
    const output = data.toString();
    if (!output.includes('INFO') && !output.includes('WARNING')) {
      console.error('Backend stderr:', output);
    }
  });
  
  backendProcess.on('error', (error) => {
    console.error('Backend process error:', error);
  });
  
  // Wait for backend to be ready
  await waitForService(BACKEND_URL);
  
  console.log('✓ Backend server ready for integration tests');
}

/**
 * Setup test data in the database
 */
async function setupTestData(): Promise<void> {
  console.log('📊 Setting up test data...');
  
  try {
    // Create test user
    const createUserResponse = await fetch(`${BACKEND_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'testpassword123',
        full_name: 'Test User',
      }),
    });
    
    if (!createUserResponse.ok && createUserResponse.status !== 409) {
      // 409 means user already exists, which is fine
      console.warn('Failed to create test user:', await createUserResponse.text());
    }
    
    // Add more test data setup as needed
    console.log('✓ Test data setup complete');
  } catch (error) {
    console.warn('Test data setup failed (continuing anyway):', error);
  }
}

/**
 * Global setup function called by Jest
 */
export default async function globalSetup(): Promise<void> {
  console.log('🧪 Setting up integration test environment...');
  
  try {
    // Start database
    await startTestDatabase();
    
    // Start backend server
    await startBackendServer();
    
    // Setup test data
    await setupTestData();
    
    // Store backend URL for tests
    process.env.INTEGRATION_BACKEND_URL = BACKEND_URL;
    
    console.log('✅ Integration test environment ready!');
    console.log(`   Backend URL: ${BACKEND_URL}`);
    console.log(`   Health check: ${BACKEND_URL}/health`);
    
  } catch (error) {
    console.error('❌ Failed to setup integration test environment:', error);
    
    // Cleanup on failure
    if (backendProcess) {
      backendProcess.kill();
    }
    if (dbProcess) {
      dbProcess.kill();
    }
    
    throw error;
  }
}

// Export for cleanup
export { backendProcess, dbProcess };
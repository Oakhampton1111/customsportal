/**
 * Test environment configuration for integration tests
 */

export interface TestEnvironmentConfig {
  backendUrl: string;
  apiTimeout: number;
  retryAttempts: number;
  retryDelay: number;
  testUser: {
    email: string;
    password: string;
    fullName: string;
  };
  database: {
    name: string;
    host: string;
    port: number;
    user: string;
    password: string;
  };
}

/**
 * Get test environment configuration
 */
export function getTestEnvironmentConfig(): TestEnvironmentConfig {
  return {
    backendUrl: process.env.INTEGRATION_BACKEND_URL || 'http://localhost:8001',
    apiTimeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000, // 1 second
    testUser: {
      email: 'test@example.com',
      password: 'testpassword123',
      fullName: 'Test User',
    },
    database: {
      name: 'customs_broker_portal_test',
      host: process.env.PGHOST || 'localhost',
      port: parseInt(process.env.PGPORT || '5432'),
      user: process.env.PGUSER || 'postgres',
      password: process.env.PGPASSWORD || 'password',
    },
  };
}

/**
 * Check if we're running in integration test mode
 */
export function isIntegrationTestMode(): boolean {
  return process.env.NODE_ENV === 'test' && !!process.env.INTEGRATION_BACKEND_URL;
}

/**
 * Get API base URL for tests
 */
export function getApiBaseUrl(): string {
  const config = getTestEnvironmentConfig();
  return `${config.backendUrl}/api`;
}

/**
 * Get authentication headers for API requests
 */
export function getAuthHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  return headers;
}

/**
 * Wait for a condition to be true with timeout
 */
export async function waitForCondition(
  condition: () => Promise<boolean> | boolean,
  timeout: number = 10000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error(`Condition not met within ${timeout}ms`);
}

/**
 * Retry an async operation with exponential backoff
 */
export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxAttempts: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxAttempts) {
        break;
      }
      
      const delay = baseDelay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError!;
}

/**
 * Generate unique test data identifiers
 */
export function generateTestId(prefix: string = 'test'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Clean up test data after tests
 */
export async function cleanupTestData(testIds: string[]): Promise<void> {
  // This would typically clean up any test data created during tests
  // Implementation depends on your specific cleanup needs
  console.log('Cleaning up test data:', testIds);
}
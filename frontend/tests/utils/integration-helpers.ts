/**
 * Helper utilities for integration tests
 */

import { apiClient } from './api-client';
import { getTestEnvironmentConfig, generateTestId, waitForCondition } from '../config/test-environment';

export interface TestUser {
  email: string;
  password: string;
  fullName: string;
  token?: string;
  id?: string;
}

export interface TestData {
  users: TestUser[];
  tariffCodes: string[];
  testIds: string[];
}

/**
 * Setup test data for integration tests
 */
export async function setupIntegrationTestData(): Promise<TestData> {
  const config = getTestEnvironmentConfig();
  const testData: TestData = {
    users: [],
    tariffCodes: ['0101.10.00', '0102.21.00', '8471.30.00', '9403.10.00'],
    testIds: [],
  };

  // Create test users
  const testUsers = [
    {
      email: config.testUser.email,
      password: config.testUser.password,
      fullName: config.testUser.fullName,
    },
    {
      email: `test2_${generateTestId()}@example.com`,
      password: 'testpassword456',
      fullName: 'Test User 2',
    },
  ];

  for (const userData of testUsers) {
    try {
      const result = await apiClient.register(userData.email, userData.password, userData.fullName);
      testData.users.push({
        ...userData,
        token: result.token,
        id: result.user?.id,
      });
      testData.testIds.push(userData.email);
    } catch {
      // User might already exist, try to login
      try {
        const result = await apiClient.login(userData.email, userData.password);
        testData.users.push({
          ...userData,
          token: result.token,
          id: result.user?.id,
        });
      } catch (loginError) {
        console.warn(`Failed to create/login test user ${userData.email}:`, loginError);
      }
    }
  }

  return testData;
}

/**
 * Cleanup test data after tests
 */
export async function cleanupIntegrationTestData(testData: TestData): Promise<void> {
  // Logout all test users
  for (const user of testData.users) {
    if (user.token) {
      try {
        apiClient.setAuthToken(user.token);
        await apiClient.logout();
      } catch (error) {
        console.warn(`Failed to logout user ${user.email}:`, error);
      }
    }
  }

  // Clear any remaining auth tokens
  apiClient.clearAuthToken();

  console.log('Integration test data cleaned up');
}

/**
 * Wait for backend to be ready
 */
export async function waitForBackendReady(timeout: number = 30000): Promise<void> {
  await waitForCondition(async () => {
    try {
      await apiClient.healthCheck();
      return true;
    } catch {
      return false;
    }
  }, timeout, 1000);
}

/**
 * Authenticate as test user
 */
export async function authenticateTestUser(userIndex: number = 0): Promise<TestUser> {
  const config = getTestEnvironmentConfig();
  const testUser = {
    email: userIndex === 0 ? config.testUser.email : `test${userIndex + 1}_${generateTestId()}@example.com`,
    password: config.testUser.password,
    fullName: `Test User ${userIndex + 1}`,
  };

  try {
    const result = await apiClient.login(testUser.email, testUser.password);
    return {
      ...testUser,
      token: result.token,
      id: result.user?.id,
    };
  } catch {
    // User doesn't exist, create it
    const result = await apiClient.register(testUser.email, testUser.password, testUser.fullName);
    return {
      ...testUser,
      token: result.token,
      id: result.user?.id,
    };
  }
}

/**
 * Create test tariff data
 */
export function createTestTariffData() {
  return {
    sections: [
      {
        id: '01',
        title: 'Live animals; animal products',
        chapters: ['01', '02', '03', '04', '05'],
      },
      {
        id: '16',
        title: 'Machines and mechanical appliances; electrical equipment',
        chapters: ['84', '85'],
      },
    ],
    chapters: [
      {
        id: '01',
        title: 'Live animals',
        section_id: '01',
      },
      {
        id: '84',
        title: 'Nuclear reactors, boilers, machinery and mechanical appliances',
        section_id: '16',
      },
    ],
    tariffCodes: [
      {
        hs_code: '0101.10.00',
        description: 'Horses - Pure-bred breeding animals',
        general_rate: '0%',
        gst_rate: '10%',
      },
      {
        hs_code: '8471.30.00',
        description: 'Portable automatic data processing machines',
        general_rate: '0%',
        gst_rate: '10%',
      },
    ],
  };
}

/**
 * Create test duty calculation data
 */
export function createTestDutyData() {
  return {
    calculations: [
      {
        hs_code: '0101.10.00',
        value: 10000,
        country_code: 'US',
        expected_duty: 0,
        expected_gst: 1000,
      },
      {
        hs_code: '8471.30.00',
        value: 2000,
        country_code: 'CN',
        expected_duty: 0,
        expected_gst: 200,
      },
    ],
  };
}

/**
 * Create test search data
 */
export function createTestSearchData() {
  return {
    products: [
      {
        description: 'laptop computer',
        expected_hs_codes: ['8471.30.00', '8471.41.00'],
      },
      {
        description: 'horse for breeding',
        expected_hs_codes: ['0101.10.00'],
      },
      {
        description: 'wooden table',
        expected_hs_codes: ['9403.10.00', '9403.60.00'],
      },
    ],
    queries: [
      'computer',
      'animal',
      'furniture',
      'machinery',
    ],
  };
}

/**
 * Validate API response structure
 */
export function validateApiResponse(response: unknown, expectedFields: string[]): void {
  expect(response).toBeDefined();
  expect(typeof response).toBe('object');
  expect(response).not.toBeNull();

  const responseObj = response as Record<string, unknown>;
  
  for (const field of expectedFields) {
    expect(responseObj).toHaveProperty(field);
  }
}

/**
 * Validate tariff code format
 */
export function validateTariffCode(hsCode: string): void {
  expect(hsCode).toMatch(/^\d{4}\.\d{2}\.\d{2}$/);
}

/**
 * Validate duty calculation response
 */
export function validateDutyCalculation(calculation: unknown): void {
  validateApiResponse(calculation, [
    'hs_code',
    'total_duty',
    'breakdown',
    'effective_rate',
  ]);

  const calc = calculation as Record<string, unknown>;
  expect(typeof calc.total_duty).toBe('number');
  expect(calc.total_duty).toBeGreaterThanOrEqual(0);
  expect(Array.isArray(calc.breakdown)).toBe(true);
}

/**
 * Validate classification response
 */
export function validateClassificationResponse(classification: unknown): void {
  validateApiResponse(classification, [
    'hs_code',
    'confidence',
    'description',
  ]);

  const classif = classification as Record<string, unknown>;
  expect(typeof classif.confidence).toBe('number');
  expect(classif.confidence).toBeGreaterThanOrEqual(0);
  expect(classif.confidence).toBeLessThanOrEqual(1);
  validateTariffCode(classif.hs_code as string);
}

/**
 * Measure API response time
 */
export async function measureResponseTime<T>(
  operation: () => Promise<T>
): Promise<{ result: T; responseTime: number }> {
  const startTime = Date.now();
  const result = await operation();
  const responseTime = Date.now() - startTime;
  
  return { result, responseTime };
}

/**
 * Test API endpoint with retries
 */
export async function testApiEndpoint<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  expectedMaxResponseTime?: number
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const { result, responseTime } = await measureResponseTime(operation);
      
      if (expectedMaxResponseTime && responseTime > expectedMaxResponseTime) {
        console.warn(`API response time ${responseTime}ms exceeds expected ${expectedMaxResponseTime}ms`);
      }
      
      return result;
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        break;
      }
      
      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
  
  throw lastError!;
}

/**
 * Generate test performance metrics
 */
export interface PerformanceMetrics {
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  successRate: number;
  totalRequests: number;
}

export async function measureApiPerformance<T>(
  operation: () => Promise<T>,
  iterations: number = 10
): Promise<PerformanceMetrics> {
  const responseTimes: number[] = [];
  let successCount = 0;
  
  for (let i = 0; i < iterations; i++) {
    try {
      const { responseTime } = await measureResponseTime(operation);
      responseTimes.push(responseTime);
      successCount++;
    } catch (error) {
      console.warn(`Performance test iteration ${i + 1} failed:`, error);
    }
  }
  
  return {
    averageResponseTime: responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length,
    minResponseTime: Math.min(...responseTimes),
    maxResponseTime: Math.max(...responseTimes),
    successRate: successCount / iterations,
    totalRequests: iterations,
  };
}
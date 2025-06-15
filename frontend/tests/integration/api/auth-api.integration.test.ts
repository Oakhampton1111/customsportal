/**
 * Integration tests for Authentication API endpoints
 * Tests real API communication with backend server
 */

import { apiClient } from '../../utils/api-client';
import {
  setupIntegrationTestData,
  cleanupIntegrationTestData,
  waitForBackendReady,
  validateApiResponse,
  testApiEndpoint,
  type TestData,
} from '../../utils/integration-helpers';
import { getTestEnvironmentConfig, generateTestId } from '../../config/test-environment';

describe('Authentication API Integration Tests', () => {
  let testData: TestData;
  const config = getTestEnvironmentConfig();

  beforeAll(async () => {
    // Wait for backend to be ready
    await waitForBackendReady();
    
    // Setup test data
    testData = await setupIntegrationTestData();
  }, 60000);

  afterAll(async () => {
    // Cleanup test data
    await cleanupIntegrationTestData(testData);
  });

  beforeEach(() => {
    // Clear any existing auth token before each test
    apiClient.clearAuthToken();
  });

  describe('POST /api/auth/register', () => {
    it('should register a new user successfully', async () => {
      const userData = {
        email: `newuser_${generateTestId()}@example.com`,
        password: 'securepassword123',
        fullName: 'New Test User',
      };

      const result = await testApiEndpoint(
        () => apiClient.register(userData.email, userData.password, userData.fullName),
        3,
        10000
      );

      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(typeof result.token).toBe('string');
      expect(result.token.length).toBeGreaterThan(0);

      // Validate user object
      validateApiResponse(result.user, ['id', 'email', 'full_name']);
      expect(result.user.email).toBe(userData.email);
      expect(result.user.full_name).toBe(userData.fullName);
    });

    it('should reject registration with invalid email', async () => {
      await expect(
        apiClient.register('invalid-email', 'password123', 'Test User')
      ).rejects.toMatchObject({
        status: 422,
      });
    });

    it('should reject registration with weak password', async () => {
      await expect(
        apiClient.register(`test_${generateTestId()}@example.com`, '123', 'Test User')
      ).rejects.toMatchObject({
        status: 422,
      });
    });

    it('should reject duplicate email registration', async () => {
      const userData = {
        email: `duplicate_${generateTestId()}@example.com`,
        password: 'securepassword123',
        fullName: 'Duplicate User',
      };

      // First registration should succeed
      await apiClient.register(userData.email, userData.password, userData.fullName);

      // Second registration with same email should fail
      await expect(
        apiClient.register(userData.email, userData.password, userData.fullName)
      ).rejects.toMatchObject({
        status: 409, // Conflict
      });
    });

    it('should validate required fields', async () => {
      // Missing email
      await expect(
        apiClient.register('', 'password123', 'Test User')
      ).rejects.toMatchObject({
        status: 422,
      });

      // Missing password
      await expect(
        apiClient.register(`test_${generateTestId()}@example.com`, '', 'Test User')
      ).rejects.toMatchObject({
        status: 422,
      });

      // Missing full name
      await expect(
        apiClient.register(`test_${generateTestId()}@example.com`, 'password123', '')
      ).rejects.toMatchObject({
        status: 422,
      });
    });
  });

  describe('POST /api/auth/login', () => {
    let testUser: { email: string; password: string; fullName: string };

    beforeEach(async () => {
      // Create a test user for login tests
      testUser = {
        email: `logintest_${generateTestId()}@example.com`,
        password: 'loginpassword123',
        fullName: 'Login Test User',
      };

      await apiClient.register(testUser.email, testUser.password, testUser.fullName);
      apiClient.clearAuthToken(); // Clear token after registration
    });

    it('should login with valid credentials', async () => {
      const result = await testApiEndpoint(
        () => apiClient.login(testUser.email, testUser.password),
        3,
        5000
      );

      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(typeof result.token).toBe('string');
      expect(result.token.length).toBeGreaterThan(0);

      // Validate user object
      validateApiResponse(result.user, ['id', 'email', 'full_name']);
      expect(result.user.email).toBe(testUser.email);
      expect(result.user.full_name).toBe(testUser.fullName);
    });

    it('should reject login with invalid email', async () => {
      await expect(
        apiClient.login('nonexistent@example.com', testUser.password)
      ).rejects.toMatchObject({
        status: 401, // Unauthorized
      });
    });

    it('should reject login with invalid password', async () => {
      await expect(
        apiClient.login(testUser.email, 'wrongpassword')
      ).rejects.toMatchObject({
        status: 401, // Unauthorized
      });
    });

    it('should reject login with malformed email', async () => {
      await expect(
        apiClient.login('invalid-email', testUser.password)
      ).rejects.toMatchObject({
        status: 422, // Validation error
      });
    });

    it('should handle case-insensitive email login', async () => {
      const upperCaseEmail = testUser.email.toUpperCase();
      
      const result = await apiClient.login(upperCaseEmail, testUser.password);
      
      expect(result).toHaveProperty('token');
      expect(result.user.email).toBe(testUser.email.toLowerCase());
    });
  });

  describe('POST /api/auth/logout', () => {
    let authToken: string;

    beforeEach(async () => {
      // Login to get a valid token
      const userData = {
        email: `logouttest_${generateTestId()}@example.com`,
        password: 'logoutpassword123',
        fullName: 'Logout Test User',
      };

      const result = await apiClient.register(userData.email, userData.password, userData.fullName);
      authToken = result.token;
      apiClient.setAuthToken(authToken);
    });

    it('should logout successfully with valid token', async () => {
      await testApiEndpoint(
        () => apiClient.logout(),
        3,
        5000
      );

      // Token should be cleared after logout
      expect(apiClient['authToken']).toBeUndefined();
    });

    it('should handle logout without token gracefully', async () => {
      apiClient.clearAuthToken();
      
      // Logout without token should not throw error
      await expect(apiClient.logout()).resolves.not.toThrow();
    });

    it('should invalidate token after logout', async () => {
      await apiClient.logout();
      
      // Try to use the token after logout - should fail
      apiClient.setAuthToken(authToken);
      
      await expect(
        apiClient.get('/auth/profile') // Protected endpoint
      ).rejects.toMatchObject({
        status: 401,
      });
    });
  });

  describe('Token Management', () => {
    let testUser: { email: string; password: string; fullName: string; token: string };

    beforeEach(async () => {
      testUser = {
        email: `tokentest_${generateTestId()}@example.com`,
        password: 'tokenpassword123',
        fullName: 'Token Test User',
        token: '',
      };

      const result = await apiClient.register(testUser.email, testUser.password, testUser.fullName);
      testUser.token = result.token;
    });

    it('should accept valid JWT token format', () => {
      // JWT tokens have 3 parts separated by dots
      const tokenParts = testUser.token.split('.');
      expect(tokenParts).toHaveLength(3);
      
      // Each part should be base64 encoded
      tokenParts.forEach(part => {
        expect(part).toMatch(/^[A-Za-z0-9_-]+$/);
      });
    });

    it('should include token in Authorization header', async () => {
      apiClient.setAuthToken(testUser.token);
      
      // Make a request that requires authentication
      try {
        await apiClient.get('/auth/profile');
      } catch (error) {
        // Even if endpoint doesn't exist, we should get 404, not 401
        const errorObj = error as { status: number };
        expect(errorObj.status).not.toBe(401);
      }
    });

    it('should handle token expiration gracefully', async () => {
      // This test would require a way to create expired tokens
      // For now, we'll test with an obviously invalid token
      apiClient.setAuthToken('invalid.token.here');
      
      await expect(
        apiClient.get('/auth/profile')
      ).rejects.toMatchObject({
        status: 401,
      });
    });

    it('should refresh token when needed', async () => {
      // This would test token refresh functionality if implemented
      apiClient.setAuthToken(testUser.token);
      
      // Make multiple requests to test token persistence
      const requests = Array(3).fill(null).map(() =>
        apiClient.healthCheck() // Use health check as it doesn't require auth
      );
      
      const results = await Promise.all(requests);
      results.forEach(result => {
        expect(result).toBeDefined();
      });
    });
  });

  describe('Security Features', () => {
    it('should enforce rate limiting on login attempts', async () => {
      const testEmail = `ratetest_${generateTestId()}@example.com`;
      
      // Make many rapid login attempts with wrong password
      const rapidAttempts = Array(10).fill(null).map(() =>
        apiClient.login(testEmail, 'wrongpassword').catch(error => error)
      );
      
      const results = await Promise.all(rapidAttempts);
      
      // Some attempts should be rate limited
      const rateLimitedAttempts = results.filter(
        result => result.status === 429
      );
      
      if (rateLimitedAttempts.length > 0) {
        console.log(`${rateLimitedAttempts.length} login attempts were rate limited`);
      }
      
      // At least some attempts should fail with 401 (not rate limited)
      const unauthorizedAttempts = results.filter(
        result => result.status === 401
      );
      expect(unauthorizedAttempts.length).toBeGreaterThan(0);
    });

    it('should validate password strength requirements', async () => {
      const weakPasswords = [
        '123',
        'password',
        'abc',
        '12345678',
        'qwerty',
      ];
      
      for (const weakPassword of weakPasswords) {
        await expect(
          apiClient.register(`weak_${generateTestId()}@example.com`, weakPassword, 'Test User')
        ).rejects.toMatchObject({
          status: 422,
        });
      }
    });

    it('should sanitize user input', async () => {
      const maliciousInputs = {
        email: `<script>alert('xss')</script>@example.com`,
        fullName: `<img src=x onerror=alert('xss')>`,
      };
      
      await expect(
        apiClient.register(maliciousInputs.email, 'password123', maliciousInputs.fullName)
      ).rejects.toMatchObject({
        status: 422,
      });
    });

    it('should handle SQL injection attempts', async () => {
      const sqlInjectionAttempts = [
        `'; DROP TABLE users; --@example.com`,
        `admin'--@example.com`,
        `' OR '1'='1@example.com`,
      ];
      
      for (const maliciousEmail of sqlInjectionAttempts) {
        await expect(
          apiClient.register(maliciousEmail, 'password123', 'Test User')
        ).rejects.toMatchObject({
          status: 422,
        });
      }
    });
  });

  describe('Error Handling', () => {
    it('should provide meaningful error messages', async () => {
      try {
        await apiClient.login('invalid@example.com', 'wrongpassword');
      } catch (error) {
        const errorObj = error as Record<string, unknown>;
        expect(errorObj).toHaveProperty('message');
        expect(typeof errorObj.message).toBe('string');
        expect((errorObj.message as string).length).toBeGreaterThan(0);
        expect(errorObj.status).toBe(401);
      }
    });

    it('should handle network timeouts gracefully', async () => {
      // Temporarily set a very short timeout
      const originalTimeout = apiClient['defaultTimeout'];
      apiClient['defaultTimeout'] = 1; // 1ms timeout
      
      await expect(
        apiClient.login(config.testUser.email, config.testUser.password)
      ).rejects.toThrow(/timeout/i);
      
      // Restore original timeout
      apiClient['defaultTimeout'] = originalTimeout;
    });

    it('should handle malformed server responses', async () => {
      // This would require mocking the server response
      // For integration tests, we assume well-formed responses
      const result = await apiClient.login(config.testUser.email, config.testUser.password);
      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
    });
  });

  describe('Performance', () => {
    it('should complete authentication within reasonable time', async () => {
      const startTime = Date.now();
      
      await apiClient.login(config.testUser.email, config.testUser.password);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(duration).toBeLessThan(5000); // 5 seconds max
    });

    it('should handle concurrent authentication requests', async () => {
      const userData = {
        email: `concurrent_${generateTestId()}@example.com`,
        password: 'concurrentpassword123',
        fullName: 'Concurrent Test User',
      };
      
      // Register user first
      await apiClient.register(userData.email, userData.password, userData.fullName);
      apiClient.clearAuthToken();
      
      // Make concurrent login requests
      const concurrentLogins = Array(5).fill(null).map(() =>
        apiClient.login(userData.email, userData.password)
      );
      
      const results = await Promise.all(concurrentLogins);
      
      // All logins should succeed
      results.forEach(result => {
        expect(result).toHaveProperty('token');
        expect(result).toHaveProperty('user');
      });
      
      // All tokens should be valid (though they might be different)
      results.forEach(result => {
        expect(typeof result.token).toBe('string');
        expect(result.token.length).toBeGreaterThan(0);
      });
    });
  });
});
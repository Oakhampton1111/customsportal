/**
 * E2E Test Data Management
 * Provides utilities for managing test data across E2E tests
 */

export interface TestUser {
  id: string;
  email: string;
  password: string;
  name: string;
  role: 'broker' | 'admin' | 'user';
}

export interface TestTariff {
  hsCode: string;
  description: string;
  dutyRate: number;
  gstRate: number;
  category: string;
}

export interface TestDutyCalculation {
  hsCode: string;
  value: number;
  quantity: number;
  country: string;
  expectedDuty: number;
  expectedGst: number;
  expectedTotal: number;
}

/**
 * Test Users for different scenarios
 */
export const TEST_USERS: Record<string, TestUser> = {
  broker: {
    id: 'test-broker-001',
    email: 'broker@test.com',
    password: 'TestPassword123!',
    name: 'Test Broker',
    role: 'broker'
  },
  admin: {
    id: 'test-admin-001',
    email: 'admin@test.com',
    password: 'AdminPassword123!',
    name: 'Test Admin',
    role: 'admin'
  },
  user: {
    id: 'test-user-001',
    email: 'user@test.com',
    password: 'UserPassword123!',
    name: 'Test User',
    role: 'user'
  }
};

/**
 * Test Tariff Data
 */
export const TEST_TARIFFS: Record<string, TestTariff> = {
  electronics: {
    hsCode: '8517.12.00',
    description: 'Telephones for cellular networks',
    dutyRate: 0.05,
    gstRate: 0.10,
    category: 'Electronics'
  },
  textiles: {
    hsCode: '6109.10.00',
    description: 'T-shirts, singlets and other vests of cotton',
    dutyRate: 0.17,
    gstRate: 0.10,
    category: 'Textiles'
  },
  machinery: {
    hsCode: '8471.30.00',
    description: 'Portable automatic data processing machines',
    dutyRate: 0.00,
    gstRate: 0.10,
    category: 'Machinery'
  }
};

/**
 * Test Duty Calculations
 */
export const TEST_CALCULATIONS: Record<string, TestDutyCalculation> = {
  smartphone: {
    hsCode: '8517.12.00',
    value: 1000,
    quantity: 1,
    country: 'China',
    expectedDuty: 50,
    expectedGst: 105,
    expectedTotal: 1155
  },
  tshirts: {
    hsCode: '6109.10.00',
    value: 500,
    quantity: 10,
    country: 'Bangladesh',
    expectedDuty: 85,
    expectedGst: 58.5,
    expectedTotal: 643.5
  },
  laptop: {
    hsCode: '8471.30.00',
    value: 2000,
    quantity: 1,
    country: 'Taiwan',
    expectedDuty: 0,
    expectedGst: 200,
    expectedTotal: 2200
  }
};

/**
 * Test Countries
 */
export const TEST_COUNTRIES = [
  'Australia',
  'China',
  'United States',
  'Japan',
  'Germany',
  'United Kingdom',
  'South Korea',
  'Taiwan',
  'Singapore',
  'Thailand',
  'Vietnam',
  'Bangladesh',
  'India',
  'Indonesia'
];

/**
 * Test Search Queries
 */
export const TEST_SEARCH_QUERIES = {
  valid: [
    'mobile phone',
    'cotton t-shirt',
    'laptop computer',
    'automotive parts',
    'steel products'
  ],
  invalid: [
    '',
    'x',
    '!@#$%',
    'very long search query that exceeds normal limits and should be handled appropriately'
  ],
  partial: [
    'mob',
    'cott',
    'lap',
    'auto',
    'ste'
  ]
};

/**
 * Performance Test Data
 */
export const PERFORMANCE_TEST_DATA = {
  largeDataset: {
    itemCount: 1000,
    searchResults: 50,
    calculationsPerMinute: 100
  },
  stressTest: {
    concurrentUsers: 10,
    actionsPerUser: 20,
    timeoutMs: 30000
  }
};

/**
 * Utility class for managing test data
 */
export class TestDataManager {
  /**
   * Generate a unique test user
   */
  static generateTestUser(role: TestUser['role'] = 'user'): TestUser {
    const timestamp = Date.now();
    return {
      id: `test-${role}-${timestamp}`,
      email: `test-${role}-${timestamp}@example.com`,
      password: 'TestPassword123!',
      name: `Test ${role.charAt(0).toUpperCase() + role.slice(1)} ${timestamp}`,
      role
    };
  }

  /**
   * Generate test calculation data
   */
  static generateTestCalculation(overrides: Partial<TestDutyCalculation> = {}): TestDutyCalculation {
    const base: TestDutyCalculation = {
      hsCode: '8517.12.00',
      value: Math.floor(Math.random() * 10000) + 100,
      quantity: Math.floor(Math.random() * 10) + 1,
      country: TEST_COUNTRIES[Math.floor(Math.random() * TEST_COUNTRIES.length)],
      expectedDuty: 0,
      expectedGst: 0,
      expectedTotal: 0
    };

    const calculation = { ...base, ...overrides };
    
    // Calculate expected values based on test tariff data
    const tariff = Object.values(TEST_TARIFFS).find(t => t.hsCode === calculation.hsCode);
    if (tariff) {
      calculation.expectedDuty = calculation.value * tariff.dutyRate;
      calculation.expectedGst = (calculation.value + calculation.expectedDuty) * tariff.gstRate;
      calculation.expectedTotal = calculation.value + calculation.expectedDuty + calculation.expectedGst;
    }

    return calculation;
  }

  /**
   * Clean up test data
   */
  static async cleanup(): Promise<void> {
    // This would typically clean up any test data created during tests
    // For now, we'll just log the cleanup action
    console.log('🧹 Cleaning up test data...');
    
    // In a real implementation, this might:
    // - Clear test user accounts
    // - Remove test calculations
    // - Reset application state
    // - Clear local storage/session storage
  }

  /**
   * Seed test data for specific test scenarios
   */
  static async seedTestData(scenario: 'basic' | 'performance' | 'stress'): Promise<void> {
    console.log(`🌱 Seeding test data for ${scenario} scenario...`);
    
    switch (scenario) {
      case 'basic':
        // Seed basic test data
        break;
      case 'performance':
        // Seed large dataset for performance testing
        break;
      case 'stress':
        // Seed data for stress testing
        break;
    }
  }

  /**
   * Validate test data integrity
   */
  static validateTestData(): boolean {
    // Validate that all test data is properly structured
    const users = Object.values(TEST_USERS);
    const tariffs = Object.values(TEST_TARIFFS);
    const calculations = Object.values(TEST_CALCULATIONS);

    // Check users
    for (const user of users) {
      if (!user.id || !user.email || !user.password || !user.name || !user.role) {
        console.error('Invalid user data:', user);
        return false;
      }
    }

    // Check tariffs
    for (const tariff of tariffs) {
      if (!tariff.hsCode || !tariff.description || tariff.dutyRate < 0 || tariff.gstRate < 0) {
        console.error('Invalid tariff data:', tariff);
        return false;
      }
    }

    // Check calculations
    for (const calc of calculations) {
      if (!calc.hsCode || calc.value <= 0 || calc.quantity <= 0 || !calc.country) {
        console.error('Invalid calculation data:', calc);
        return false;
      }
    }

    return true;
  }
}

/**
 * Test data validation
 */
if (!TestDataManager.validateTestData()) {
  throw new Error('Test data validation failed');
}
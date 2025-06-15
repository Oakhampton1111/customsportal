// Mock data factories for testing

export interface MockTariffData {
  id: string;
  hsCode: string;
  description: string;
  dutyRate: number;
  gstRate: number;
  country: string;
  category?: string;
  subCategory?: string;
  unit?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface MockDutyCalculation {
  id: string;
  hsCode: string;
  description: string;
  value: number;
  country: string;
  dutyRate: number;
  dutyAmount: number;
  gstRate: number;
  gstAmount: number;
  totalAmount: number;
  calculatedAt: string;
  currency: string;
}

export interface MockSearchResult {
  id: string;
  hsCode: string;
  description: string;
  category: string;
  relevanceScore: number;
}

export interface MockUser {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'broker';
  permissions: string[];
  createdAt: string;
}

// Tariff data factory
export class TariffDataFactory {
  static create(overrides: Partial<MockTariffData> = {}): MockTariffData {
    return {
      id: `tariff-${Math.random().toString(36).substr(2, 9)}`,
      hsCode: '1234567890',
      description: 'Test Product Description',
      dutyRate: 5.0,
      gstRate: 10.0,
      country: 'AU',
      category: 'Electronics',
      subCategory: 'Consumer Electronics',
      unit: 'Each',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...overrides,
    };
  }

  static createMany(count: number, overrides: Partial<MockTariffData> = {}): MockTariffData[] {
    return Array.from({ length: count }, (_, index) =>
      this.create({
        id: `tariff-${index + 1}`,
        hsCode: `123456789${index}`,
        description: `Test Product ${index + 1}`,
        dutyRate: 5.0 + index * 0.5,
        ...overrides,
      })
    );
  }

  static createElectronics(overrides: Partial<MockTariffData> = {}): MockTariffData {
    return this.create({
      hsCode: '8517120000',
      description: 'Smartphones and mobile phones',
      category: 'Electronics',
      subCategory: 'Telecommunications',
      dutyRate: 0.0,
      ...overrides,
    });
  }

  static createTextiles(overrides: Partial<MockTariffData> = {}): MockTariffData {
    return this.create({
      hsCode: '6203420000',
      description: 'Men\'s or boys\' trousers of cotton',
      category: 'Textiles',
      subCategory: 'Clothing',
      dutyRate: 10.0,
      ...overrides,
    });
  }

  static createFood(overrides: Partial<MockTariffData> = {}): MockTariffData {
    return this.create({
      hsCode: '0406100000',
      description: 'Fresh cheese, unripened or uncured',
      category: 'Food',
      subCategory: 'Dairy Products',
      dutyRate: 0.0,
      ...overrides,
    });
  }
}

// Duty calculation factory
export class DutyCalculationFactory {
  static create(overrides: Partial<MockDutyCalculation> = {}): MockDutyCalculation {
    const value = overrides.value || 1000;
    const dutyRate = overrides.dutyRate || 5.0;
    const gstRate = overrides.gstRate || 10.0;
    const dutyAmount = (value * dutyRate) / 100;
    const gstAmount = ((value + dutyAmount) * gstRate) / 100;
    const totalAmount = value + dutyAmount + gstAmount;

    return {
      id: `calc-${Math.random().toString(36).substr(2, 9)}`,
      hsCode: '1234567890',
      description: 'Test Product',
      value,
      country: 'CN',
      dutyRate,
      dutyAmount,
      gstRate,
      gstAmount,
      totalAmount,
      calculatedAt: new Date().toISOString(),
      currency: 'AUD',
      ...overrides,
    };
  }

  static createMany(count: number, overrides: Partial<MockDutyCalculation> = {}): MockDutyCalculation[] {
    return Array.from({ length: count }, (_, index) =>
      this.create({
        id: `calc-${index + 1}`,
        hsCode: `123456789${index}`,
        value: 1000 * (index + 1),
        country: ['CN', 'US', 'JP', 'DE', 'UK'][index % 5],
        calculatedAt: new Date(Date.now() - index * 24 * 60 * 60 * 1000).toISOString(),
        ...overrides,
      })
    );
  }

  static createHighValue(overrides: Partial<MockDutyCalculation> = {}): MockDutyCalculation {
    return this.create({
      value: 50000,
      dutyRate: 15.0,
      ...overrides,
    });
  }

  static createLowValue(overrides: Partial<MockDutyCalculation> = {}): MockDutyCalculation {
    return this.create({
      value: 100,
      dutyRate: 0.0,
      ...overrides,
    });
  }
}

// Search result factory
export class SearchResultFactory {
  static create(overrides: Partial<MockSearchResult> = {}): MockSearchResult {
    return {
      id: `search-${Math.random().toString(36).substr(2, 9)}`,
      hsCode: '1234567890',
      description: 'Test Search Result',
      category: 'Electronics',
      relevanceScore: 0.95,
      ...overrides,
    };
  }

  static createMany(count: number, overrides: Partial<MockSearchResult> = {}): MockSearchResult[] {
    return Array.from({ length: count }, (_, index) =>
      this.create({
        id: `search-${index + 1}`,
        hsCode: `123456789${index}`,
        description: `Search Result ${index + 1}`,
        relevanceScore: 0.95 - index * 0.1,
        ...overrides,
      })
    );
  }

  static createRelevantResults(query: string, count = 5): MockSearchResult[] {
    return this.createMany(count, {
      description: `${query} related product`,
      relevanceScore: 0.9,
    });
  }
}

// User factory
export class UserFactory {
  static create(overrides: Partial<MockUser> = {}): MockUser {
    return {
      id: `user-${Math.random().toString(36).substr(2, 9)}`,
      name: 'Test User',
      email: 'test@example.com',
      role: 'user',
      permissions: ['read:tariffs', 'calculate:duties'],
      createdAt: new Date().toISOString(),
      ...overrides,
    };
  }

  static createAdmin(overrides: Partial<MockUser> = {}): MockUser {
    return this.create({
      name: 'Admin User',
      email: 'admin@example.com',
      role: 'admin',
      permissions: [
        'read:tariffs',
        'write:tariffs',
        'calculate:duties',
        'manage:users',
        'view:analytics',
      ],
      ...overrides,
    });
  }

  static createBroker(overrides: Partial<MockUser> = {}): MockUser {
    return this.create({
      name: 'Customs Broker',
      email: 'broker@example.com',
      role: 'broker',
      permissions: [
        'read:tariffs',
        'calculate:duties',
        'submit:declarations',
        'view:client:data',
      ],
      ...overrides,
    });
  }
}

// API response factories
export class ApiResponseFactory {
  static createSuccessResponse<T>(data: T) {
    return {
      success: true,
      data,
      message: 'Operation completed successfully',
      timestamp: new Date().toISOString(),
    };
  }

  static createErrorResponse(message = 'An error occurred', code = 'GENERIC_ERROR') {
    return {
      success: false,
      error: {
        code,
        message,
        details: {},
      },
      timestamp: new Date().toISOString(),
    };
  }

  static createPaginatedResponse<T>(
    items: T[],
    page = 1,
    limit = 10,
    total?: number
  ) {
    const actualTotal = total || items.length;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedItems = items.slice(startIndex, endIndex);

    return this.createSuccessResponse({
      items: paginatedItems,
      pagination: {
        page,
        limit,
        total: actualTotal,
        totalPages: Math.ceil(actualTotal / limit),
        hasNext: endIndex < actualTotal,
        hasPrev: page > 1,
      },
    });
  }
}

// Form data factories
export class FormDataFactory {
  static createDutyCalculationForm(overrides: Record<string, string> = {}) {
    return {
      hsCode: '1234567890',
      value: '1000',
      country: 'CN',
      currency: 'AUD',
      description: 'Test Product',
      ...overrides,
    };
  }

  static createTariffSearchForm(overrides: Record<string, string> = {}) {
    return {
      query: 'smartphone',
      category: 'Electronics',
      country: 'AU',
      ...overrides,
    };
  }

  static createUserRegistrationForm(overrides: Record<string, string> = {}) {
    return {
      name: 'Test User',
      email: 'test@example.com',
      password: 'password123',
      confirmPassword: 'password123',
      role: 'user',
      ...overrides,
    };
  }
}

// Test scenarios
export class TestScenarios {
  static getEmptyState() {
    return {
      tariffs: [],
      calculations: [],
      searchResults: [],
      user: null,
    };
  }

  static getLoadingState() {
    return {
      isLoading: true,
      error: null,
      data: null,
    };
  }

  static getErrorState(message = 'Something went wrong') {
    return {
      isLoading: false,
      error: { message },
      data: null,
    };
  }

  static getSuccessState<T>(data: T) {
    return {
      isLoading: false,
      error: null,
      data,
    };
  }

  static getNetworkError() {
    return new Error('Network request failed');
  }

  static getValidationError(field: string, message: string) {
    return {
      field,
      message,
      code: 'VALIDATION_ERROR',
    };
  }
}

// Export all factories as a single object for convenience
export const MockData = {
  Tariff: TariffDataFactory,
  DutyCalculation: DutyCalculationFactory,
  SearchResult: SearchResultFactory,
  User: UserFactory,
  ApiResponse: ApiResponseFactory,
  FormData: FormDataFactory,
  Scenarios: TestScenarios,
};
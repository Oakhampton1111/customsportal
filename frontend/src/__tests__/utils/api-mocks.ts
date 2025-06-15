import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { MockData } from './mock-data';

// API base URL - should match your actual API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Mock handlers for different API endpoints
export const handlers = [
  // Tariff endpoints
  rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
    const query = req.url.searchParams.get('q') || '';
    const category = req.url.searchParams.get('category');
    const page = parseInt(req.url.searchParams.get('page') || '1');
    const limit = parseInt(req.url.searchParams.get('limit') || '10');

    let results = MockData.Tariff.createMany(25);
    
    // Filter by query
    if (query) {
      results = results.filter(tariff => 
        tariff.description.toLowerCase().includes(query.toLowerCase()) ||
        tariff.hsCode.includes(query)
      );
    }
    
    // Filter by category
    if (category) {
      results = results.filter(tariff => tariff.category === category);
    }

    const paginatedResponse = MockData.ApiResponse.createPaginatedResponse(
      results, page, limit
    );

    return res(ctx.status(200), ctx.json(paginatedResponse));
  }),

  rest.get(`${API_BASE_URL}/tariffs/:hsCode`, (req, res, ctx) => {
    const { hsCode } = req.params;
    const tariff = MockData.Tariff.create({ hsCode: hsCode as string });
    
    return res(
      ctx.status(200),
      ctx.json(MockData.ApiResponse.createSuccessResponse(tariff))
    );
  }),

  // Duty calculation endpoints
  rest.post(`${API_BASE_URL}/duty/calculate`, (req, res, ctx) => {
    const calculation = MockData.DutyCalculation.create();
    
    return res(
      ctx.status(200),
      ctx.json(MockData.ApiResponse.createSuccessResponse(calculation))
    );
  }),

  rest.get(`${API_BASE_URL}/duty/history`, (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page') || '1');
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    
    const calculations = MockData.DutyCalculation.createMany(15);
    const paginatedResponse = MockData.ApiResponse.createPaginatedResponse(
      calculations, page, limit
    );

    return res(ctx.status(200), ctx.json(paginatedResponse));
  }),

  // Search endpoints
  rest.get(`${API_BASE_URL}/search`, (req, res, ctx) => {
    const query = req.url.searchParams.get('q') || '';
    const results = MockData.SearchResult.createRelevantResults(query);
    
    return res(
      ctx.status(200),
      ctx.json(MockData.ApiResponse.createSuccessResponse(results))
    );
  }),

  // User/Auth endpoints
  rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
    const user = MockData.User.create();
    const token = 'mock-jwt-token';
    
    return res(
      ctx.status(200),
      ctx.json(MockData.ApiResponse.createSuccessResponse({ user, token }))
    );
  }),

  rest.post(`${API_BASE_URL}/auth/register`, (req, res, ctx) => {
    const user = MockData.User.create();
    
    return res(
      ctx.status(201),
      ctx.json(MockData.ApiResponse.createSuccessResponse(user))
    );
  }),

  rest.get(`${API_BASE_URL}/auth/me`, (req, res, ctx) => {
    const user = MockData.User.create();
    
    return res(
      ctx.status(200),
      ctx.json(MockData.ApiResponse.createSuccessResponse(user))
    );
  }),

  // Error scenarios
  rest.get(`${API_BASE_URL}/error/500`, (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json(MockData.ApiResponse.createErrorResponse('Internal server error', 'INTERNAL_ERROR'))
    );
  }),

  rest.get(`${API_BASE_URL}/error/404`, (req, res, ctx) => {
    return res(
      ctx.status(404),
      ctx.json(MockData.ApiResponse.createErrorResponse('Resource not found', 'NOT_FOUND'))
    );
  }),

  rest.get(`${API_BASE_URL}/error/network`, (req, res, ctx) => {
    return res.networkError('Network connection failed');
  }),
];

// Create mock server
export const server = setupServer(...handlers);

// Mock API utilities
export class MockApiUtils {
  static setupSuccessfulResponses() {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        const results = MockData.Tariff.createMany(5);
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(results))
        );
      })
    );
  }

  static setupErrorResponses() {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json(MockData.ApiResponse.createErrorResponse('Server error'))
        );
      })
    );
  }

  static setupNetworkError() {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        return res.networkError('Network connection failed');
      })
    );
  }

  static setupSlowResponse(delay = 2000) {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        const results = MockData.Tariff.createMany(5);
        return res(
          ctx.delay(delay),
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(results))
        );
      })
    );
  }

  static setupEmptyResponse() {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse([]))
        );
      })
    );
  }

  static setupValidationError() {
    server.use(
      rest.post(`${API_BASE_URL}/duty/calculate`, (req, res, ctx) => {
        return res(
          ctx.status(400),
          ctx.json(MockData.ApiResponse.createErrorResponse(
            'Validation failed',
            'VALIDATION_ERROR'
          ))
        );
      })
    );
  }

  static setupAuthError() {
    server.use(
      rest.get(`${API_BASE_URL}/auth/me`, (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json(MockData.ApiResponse.createErrorResponse(
            'Unauthorized',
            'UNAUTHORIZED'
          ))
        );
      })
    );
  }

  static resetToDefaults() {
    server.resetHandlers(...handlers);
  }
}

// Specific endpoint mocks
export class TariffApiMocks {
  static mockSearchSuccess(results = MockData.Tariff.createMany(5)) {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(results))
        );
      })
    );
  }

  static mockSearchEmpty() {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/search`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse([]))
        );
      })
    );
  }

  static mockGetTariffSuccess(hsCode: string, tariff?: any) {
    const mockTariff = tariff || MockData.Tariff.create({ hsCode });
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/${hsCode}`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(mockTariff))
        );
      })
    );
  }

  static mockGetTariffNotFound(hsCode: string) {
    server.use(
      rest.get(`${API_BASE_URL}/tariffs/${hsCode}`, (req, res, ctx) => {
        return res(
          ctx.status(404),
          ctx.json(MockData.ApiResponse.createErrorResponse('Tariff not found', 'NOT_FOUND'))
        );
      })
    );
  }
}

export class DutyApiMocks {
  static mockCalculateSuccess(calculation?: any) {
    const mockCalculation = calculation || MockData.DutyCalculation.create();
    server.use(
      rest.post(`${API_BASE_URL}/duty/calculate`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(mockCalculation))
        );
      })
    );
  }

  static mockCalculateValidationError() {
    server.use(
      rest.post(`${API_BASE_URL}/duty/calculate`, (req, res, ctx) => {
        return res(
          ctx.status(400),
          ctx.json(MockData.ApiResponse.createErrorResponse(
            'Invalid input data',
            'VALIDATION_ERROR'
          ))
        );
      })
    );
  }

  static mockHistorySuccess(calculations?: any[]) {
    const mockCalculations = calculations || MockData.DutyCalculation.createMany(10);
    server.use(
      rest.get(`${API_BASE_URL}/duty/history`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(mockCalculations))
        );
      })
    );
  }
}

export class AuthApiMocks {
  static mockLoginSuccess(user?: any) {
    const mockUser = user || MockData.User.create();
    server.use(
      rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse({
            user: mockUser,
            token: 'mock-jwt-token'
          }))
        );
      })
    );
  }

  static mockLoginFailure() {
    server.use(
      rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json(MockData.ApiResponse.createErrorResponse(
            'Invalid credentials',
            'INVALID_CREDENTIALS'
          ))
        );
      })
    );
  }

  static mockRegisterSuccess(user?: any) {
    const mockUser = user || MockData.User.create();
    server.use(
      rest.post(`${API_BASE_URL}/auth/register`, (req, res, ctx) => {
        return res(
          ctx.status(201),
          ctx.json(MockData.ApiResponse.createSuccessResponse(mockUser))
        );
      })
    );
  }

  static mockGetUserSuccess(user?: any) {
    const mockUser = user || MockData.User.create();
    server.use(
      rest.get(`${API_BASE_URL}/auth/me`, (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json(MockData.ApiResponse.createSuccessResponse(mockUser))
        );
      })
    );
  }

  static mockUnauthorized() {
    server.use(
      rest.get(`${API_BASE_URL}/auth/me`, (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json(MockData.ApiResponse.createErrorResponse(
            'Unauthorized',
            'UNAUTHORIZED'
          ))
        );
      })
    );
  }
}

// Test setup helpers
export const setupMockServer = () => {
  beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
};

export const setupMockServerQuiet = () => {
  beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
};
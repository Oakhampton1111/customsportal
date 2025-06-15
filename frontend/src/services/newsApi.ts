import axios, { AxiosError } from 'axios';

// Temporarily hardcode to test
const API_BASE_URL = 'http://127.0.0.1:8000';

// Debug logging
console.log('News API - Environment variable VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
console.log('News API - Using API_BASE_URL:', API_BASE_URL);

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`News API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('News API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`News API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('News API Response Error:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      const errorData = data as { detail?: string; message?: string };
      throw new Error(errorData?.detail || errorData?.message || `HTTP ${status} Error`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// TypeScript interfaces for News API
export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  category: string;
  source: string;
  published_date: string;
  url?: string;
  tags: string[];
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface WeeklySummary {
  week_start: string;
  week_end: string;
  total_articles: number;
  categories: Record<string, number>;
  top_stories: NewsItem[];
  trends: {
    topic: string;
    mentions: number;
    change_percent: number;
  }[];
}

export interface TradeSummary {
  period: string;
  total_trade_value: number;
  import_value: number;
  export_value: number;
  trade_balance: number;
  top_trading_partners: {
    country: string;
    trade_value: number;
    change_percent: number;
  }[];
  commodity_highlights: {
    commodity: string;
    hs_code: string;
    value: number;
    change_percent: number;
  }[];
}

export interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action_url?: string;
  expires_at?: string;
}

export interface NewsAnalytics {
  total_articles: number;
  categories_breakdown: Record<string, number>;
  sources_breakdown: Record<string, number>;
  trending_topics: {
    topic: string;
    mentions: number;
    sentiment: 'positive' | 'negative' | 'neutral';
  }[];
  time_series: {
    date: string;
    article_count: number;
  }[];
}

export const newsApi = {
  /**
   * Get dashboard news feed
   */
  async getDashboardFeed(): Promise<NewsItem[]> {
    const response = await apiClient.get<NewsItem[]>('/api/news/dashboard-feed');
    return response.data;
  },

  /**
   * Get weekly news summary
   */
  async getWeeklySummary(): Promise<WeeklySummary> {
    const response = await apiClient.get<WeeklySummary>('/api/news/statistics/weekly-summary');
    return response.data;
  },

  /**
   * Get trade summary statistics
   */
  async getTradeSummary(): Promise<TradeSummary> {
    const response = await apiClient.get<TradeSummary>('/api/news/trade-summary');
    return response.data;
  },

  /**
   * Get system alerts
   */
  async getAlerts(): Promise<SystemAlert[]> {
    const response = await apiClient.get<SystemAlert[]>('/api/news/alerts');
    return response.data;
  },

  /**
   * Get news analytics
   */
  async getAnalytics(): Promise<NewsAnalytics> {
    const response = await apiClient.get<NewsAnalytics>('/api/news/analytics');
    return response.data;
  },

  /**
   * Get recent news
   */
  async getRecentNews(limit: number = 10): Promise<NewsItem[]> {
    const response = await apiClient.get<NewsItem[]>(`/api/news/recent?limit=${limit}`);
    return response.data;
  },

  /**
   * Get specific news item by ID
   */
  async getNewsItem(newsId: string): Promise<NewsItem> {
    const response = await apiClient.get<NewsItem>(`/api/news/${newsId}`);
    return response.data;
  },

  /**
   * Health check for the news service
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/news/health');
    return response.data;
  },
};

export default newsApi;

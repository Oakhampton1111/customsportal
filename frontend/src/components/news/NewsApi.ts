import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const newsApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content?: string;
  source: string;
  category: 'tariff' | 'regulation' | 'procedure' | 'announcement' | 'alert';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  published_date: string;
  effective_date?: string;
  expiry_date?: string;
  url?: string;
  tags: string[];
  is_featured: boolean;
  is_read: boolean;
}

export interface NewsFilter {
  category?: string[];
  priority?: string[];
  source?: string[];
  date_from?: string;
  date_to?: string;
  tags?: string[];
  search?: string;
}

export interface NewsResponse {
  items: NewsItem[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export const newsApi = {
  /**
   * Get latest customs news and updates
   */
  async getNews(
    page: number = 1,
    perPage: number = 20,
    filter?: NewsFilter
  ): Promise<NewsResponse> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('per_page', perPage.toString());
    
    if (filter) {
      if (filter.category?.length) {
        filter.category.forEach(cat => params.append('category', cat));
      }
      if (filter.priority?.length) {
        filter.priority.forEach(pri => params.append('priority', pri));
      }
      if (filter.source?.length) {
        filter.source.forEach(src => params.append('source', src));
      }
      if (filter.date_from) params.append('date_from', filter.date_from);
      if (filter.date_to) params.append('date_to', filter.date_to);
      if (filter.tags?.length) {
        filter.tags.forEach(tag => params.append('tags', tag));
      }
      if (filter.search) params.append('search', filter.search);
    }

    const response = await newsApiClient.get<NewsResponse>(`/api/news?${params}`);
    return response.data;
  },

  /**
   * Get featured/urgent news items
   */
  async getFeaturedNews(): Promise<NewsItem[]> {
    const response = await newsApiClient.get<NewsItem[]>('/api/news/featured');
    return response.data;
  },

  /**
   * Get news item by ID
   */
  async getNewsItem(id: string): Promise<NewsItem> {
    const response = await newsApiClient.get<NewsItem>(`/api/news/${id}`);
    return response.data;
  },

  /**
   * Mark news item as read
   */
  async markAsRead(id: string): Promise<void> {
    await newsApiClient.post(`/api/news/${id}/read`);
  },

  /**
   * Get available news categories
   */
  async getCategories(): Promise<string[]> {
    const response = await newsApiClient.get<string[]>('/api/news/categories');
    return response.data;
  },

  /**
   * Get available news sources
   */
  async getSources(): Promise<string[]> {
    const response = await newsApiClient.get<string[]>('/api/news/sources');
    return response.data;
  },

  /**
   * Get trending tags
   */
  async getTrendingTags(): Promise<string[]> {
    const response = await newsApiClient.get<string[]>('/api/news/trending-tags');
    return response.data;
  },

  /**
   * Subscribe to news notifications
   */
  async subscribe(categories: string[], email?: string): Promise<void> {
    await newsApiClient.post('/api/news/subscribe', { categories, email });
  },

  /**
   * Health check for news service
   */
  async healthCheck(): Promise<{ status: string; last_update: string }> {
    const response = await newsApiClient.get('/api/news/health');
    return response.data;
  }
};

export default newsApi;

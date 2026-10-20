/**
 * API client with authentication support.
 * Handles token storage, refresh, and automatic header injection.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  roles: string[];
  permissions: string[];
}

class ApiClient {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiry: number | null = null;
  private user: UserResponse | null = null;
  private refreshPromise: Promise<TokenResponse> | null = null;

  constructor() {
    this.loadTokens();
  }

  /**
   * Load tokens from localStorage.
   */
  private loadTokens(): void {
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    const expiry = localStorage.getItem('token_expiry');
    this.tokenExpiry = expiry ? parseInt(expiry, 10) : null;
  }

  /**
   * Save tokens to localStorage.
   */
  private saveTokens(tokens: TokenResponse): void {
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
    this.tokenExpiry = Date.now() + tokens.expires_in * 1000;
    
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('token_expiry', this.tokenExpiry.toString());
  }

  /**
   * Clear tokens from localStorage.
   */
  private clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiry = null;
    this.user = null;
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expiry');
    localStorage.removeItem('user');
  }

  /**
   * Check if access token is expired.
   */
  private isTokenExpired(): boolean {
    if (!this.tokenExpiry) return true;
    // Consider token expired 30 seconds before actual expiry
    return Date.now() >= this.tokenExpiry - 30000;
  }

  /**
   * Login with email and password.
   */
  async login(email: string, password: string): Promise<UserResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const tokens: TokenResponse = await response.json();
    this.saveTokens(tokens);

    // Fetch user info
    return this.fetchCurrentUser();
  }

  /**
   * Logout and clear tokens.
   */
  async logout(): Promise<void> {
    if (this.accessToken) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
        });
      } catch (error) {
        // Ignore logout errors
      }
    }
    
    this.clearTokens();
  }

  /**
   * Refresh access token using refresh token.
   */
  async refreshAccessToken(): Promise<TokenResponse> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    this.refreshPromise = (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: this.refreshToken }),
        });

        if (!response.ok) {
          this.clearTokens();
          throw new Error('Token refresh failed');
        }

        const tokens: TokenResponse = await response.json();
        this.saveTokens(tokens);
        return tokens;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  /**
   * Fetch current user information.
   */
  async fetchCurrentUser(): Promise<UserResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }

    const userData: UserResponse = await response.json();
    this.user = userData;
    localStorage.setItem('user', JSON.stringify(this.user));
    return userData;
  }

  /**
   * Get current user from cache or fetch.
   */
  getCurrentUser(): UserResponse | null {
    if (this.user) return this.user;
    
    const stored = localStorage.getItem('user');
    if (stored) {
      this.user = JSON.parse(stored);
      return this.user;
    }
    
    return null;
  }

  /**
   * Get authorization headers.
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    return headers;
  }

  /**
   * Make authenticated API request with automatic token refresh.
   */
  async request<T>(
    endpoint: string,
    options: RequestInit & { params?: Record<string, any> } = {}
  ): Promise<T> {
    // Check if token needs refresh
    if (this.isTokenExpired() && this.refreshToken) {
      await this.refreshAccessToken();
    }

    // Build URL with query parameters
    let url = `${API_BASE_URL}${endpoint}`;
    if (options.params) {
      const searchParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    const headers = {
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });

    // Handle 401 - try to refresh token once
    if (response.status === 401 && this.refreshToken) {
      try {
        await this.refreshAccessToken();
        // Retry request with new token
        const retryHeaders = {
          ...this.getAuthHeaders(),
          ...options.headers,
        };
        const retryResponse = await fetch(url, { ...options, headers: retryHeaders });
        
        if (!retryResponse.ok) {
          throw new Error(await retryResponse.text());
        }
        
        return retryResponse.json();
      } catch (error) {
        this.clearTokens();
        throw error;
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  /**
   * Check if user is authenticated.
   */
  isAuthenticated(): boolean {
    return !!this.accessToken && !this.isTokenExpired();
  }

  /**
   * Check if user has a specific permission.
   */
  hasPermission(permission: string): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;
    
    // Super admin has all permissions
    if (user.roles.includes('super_admin')) return true;
    
    return user.permissions.includes(permission);
  }

  /**
   * Check if user has a specific role.
   */
  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;
    return user.roles.includes(role);
  }
}

// Singleton instance
export const apiClient = new ApiClient();
export default apiClient;

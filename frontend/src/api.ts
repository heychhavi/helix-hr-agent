import axios from 'axios';

const API_URL = 'http://localhost:3002';

interface LoginData {
  email: string;
  password: string;
  name?: string;
  company?: {
    name: string;
    industry: string;
    size: string;
    description: string;
    website: string;
  };
}

interface AuthResponse {
  token: string;
  user: {
    id: number;
    email: string;
    name?: string;
    company?: {
      name: string;
      industry: string;
      size: string;
      description: string;
      website: string;
    };
  };
}

class ApiClient {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage
    this.token = localStorage.getItem('token');
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {})
    };
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  async register(data: LoginData): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}/api/register`, data, {
      headers: this.getHeaders()
    });
    return response.data;
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}/api/login`, data, {
      headers: this.getHeaders()
    });
    return response.data;
  }

  async magicAction(action: string, sequence: string) {
    const response = await axios.post(
      `${API_URL}/api/magic_action`,
      { action, sequence },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

export const api = new ApiClient();
export default api; 
import { SecurityUtils } from './security';

export class AuthService {
  constructor() {
    this.rateLimiter = SecurityUtils.createRateLimiter(5, 300000); 
  }

  async login(credentials) {
    try {
      this.rateLimiter('login');
      if (!SecurityUtils.validateEmail(credentials.email)) {
        throw new Error('Invalid email format');
      }
      const sanitizedCredentials = {
        email: SecurityUtils.sanitizeInput(credentials.email),
        password: credentials.password 
      };
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(sanitizedCredentials),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      if (data.token) {
        SecurityUtils.setSecureToken('auth_token', data.token);
      }

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }
  async changePassword(passwordData) {
    try {
      this.rateLimiter('password_change');
      const validation = SecurityUtils.validatePassword(passwordData.newPassword);
      if (!validation.isValid) {
        const missing = Object.entries(validation.requirements)
          .filter(([key, value]) => !value)
          .map(([key]) => key);
        throw new Error(`Password requirements not met: ${missing.join(', ')}`);
      }
      const sanitizedData = {
        email: SecurityUtils.sanitizeInput(passwordData.email),
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword
      };

      const token = SecurityUtils.getSecureToken('auth_token');
      const response = await fetch('/api/auth/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(sanitizedData),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Password change failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Password change error:', error);
      throw error;
    }
  }
  async logout() {
    try {
      const token = SecurityUtils.getSecureToken('auth_token');
      
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'include'
        });
      }
      sessionStorage.clear();
      localStorage.removeItem('isAuthenticated');
      document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  isAuthenticated() {
    const token = SecurityUtils.getSecureToken('auth_token');
    return !!token;
  }
  getToken() {
    return SecurityUtils.getSecureToken('auth_token');
  }
}

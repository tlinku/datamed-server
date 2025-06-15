import CryptoJS from 'crypto-js';

export class SecurityUtils {
  static sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    
    return input
      .replace(/[<>]/g, '') 
      .replace(/javascript:/gi, '') 
      .replace(/data:/gi, '') 
      .trim();
  }
  static validatePESEL(pesel) {
    if (!pesel || pesel.length !== 11 || !/^\d{11}$/.test(pesel)) {
      return false;
    }

    const weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3];
    let sum = 0;
    
    for (let i = 0; i < 10; i++) {
      sum += parseInt(pesel[i]) * weights[i];
    }
    
    const checksum = (10 - (sum % 10)) % 10;
    return parseInt(pesel[10]) === checksum;
  }
  static validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }
  static validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
      isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar,
      requirements: {
        length: password.length >= minLength,
        uppercase: hasUpperCase,
        lowercase: hasLowerCase,
        numbers: hasNumbers,
        specialChar: hasSpecialChar
      }
    };
  }
  static setSecureToken(key, value) {
    try {
      const encrypted = CryptoJS.AES.encrypt(value, 'your-encryption-key').toString();
      sessionStorage.setItem(key, encrypted);
    } catch (error) {
      console.error('Error storing secure token:', error);
    }
  }

  static getSecureToken(key) {
    try {
      const encrypted = sessionStorage.getItem(key);
      if (!encrypted) return null;
      
      const decrypted = CryptoJS.AES.decrypt(encrypted, 'your-encryption-key');
      return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      console.error('Error retrieving secure token:', error);
      return null;
    }
  }
  static createRateLimiter(maxRequests = 10, windowMs = 60000) {
    const requests = new Map();

    return function rateLimiter(identifier) {
      const now = Date.now();
      const windowStart = now - windowMs;
      if (requests.has(identifier)) {
        const userRequests = requests.get(identifier).filter(time => time > windowStart);
        requests.set(identifier, userRequests);
      }

      const userRequests = requests.get(identifier) || [];
      
      if (userRequests.length >= maxRequests) {
        throw new Error('Rate limit exceeded. Please try again later.');
      }

      userRequests.push(now);
      requests.set(identifier, userRequests);
      
      return true;
    };
  }
  static validateFileUpload(file, maxSize = 10 * 1024 * 1024, allowedTypes = ['application/pdf']) {
    const errors = [];

    if (!file) {
      errors.push('No file selected');
      return { isValid: false, errors };
    }

    if (file.size > maxSize) {
      errors.push(`File size exceeds ${maxSize / (1024 * 1024)}MB limit`);
    }

    if (!allowedTypes.includes(file.type)) {
      errors.push(`File type not allowed. Allowed types: ${allowedTypes.join(', ')}`);
    }
    const allowedExtensions = allowedTypes.map(type => {
      if (type === 'application/pdf') return '.pdf';
      return '';
    }).filter(Boolean);

    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedExtensions.includes(fileExtension)) {
      errors.push(`File extension not allowed. Allowed extensions: ${allowedExtensions.join(', ')}`);
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
  static escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  static addCSPMeta() {
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' http://localhost:5000 http://localhost:8080;";
    document.head.appendChild(meta);
  }
}

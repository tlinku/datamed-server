// Mock Keycloak implementation for testing
// This simulates a successful authentication flow

let mockAuthenticated = false;
let mockToken = null;
let mockUser = {
  preferred_username: 'test-doctor',
  given_name: 'Test',
  family_name: 'Doctor',
  email: 'test.doctor@datamed.com'
};

// Generate a fake JWT-like token
const generateMockToken = () => {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    sub: 'test-user-id-123',
    preferred_username: mockUser.preferred_username,
    given_name: mockUser.given_name,
    family_name: mockUser.family_name,
    email: mockUser.email,
    realm_access: { roles: ['doctor', 'user'] },
    exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
    iat: Math.floor(Date.now() / 1000)
  }));
  const signature = btoa('mock-signature');
  return `${header}.${payload}.${signature}`;
};

export const initKeycloak = (onAuthenticatedCallback) => {
  console.log('MOCK: Starting Keycloak initialization...');
  console.log('MOCK: Current URL:', window.location.href);
  
  // Check if we're returning from a "login"
  const url = new URL(window.location.href);
  const loginSuccess = url.searchParams.get('mock_login') === 'success';
  
  if (loginSuccess) {
    console.log('MOCK: Detected successful login redirect');
    mockAuthenticated = true;
    mockToken = generateMockToken();
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('mockToken', mockToken);
    
    // Clean the URL
    window.history.replaceState({}, document.title, window.location.origin);
  } else {
    // Check localStorage for existing session
    const storedAuth = localStorage.getItem('isAuthenticated');
    const storedToken = localStorage.getItem('mockToken');
    
    if (storedAuth === 'true' && storedToken) {
      console.log('MOCK: Found existing session');
      mockAuthenticated = true;
      mockToken = storedToken;
    }
  }
  
  // Simulate async initialization
  setTimeout(() => {
    console.log('MOCK: Keycloak init success, authenticated:', mockAuthenticated);
    console.log('MOCK: Token:', mockToken ? 'Present (length: ' + mockToken.length + ')' : 'Missing');
    onAuthenticatedCallback();
  }, 500); // Small delay to simulate real behavior
};

export const doLogin = () => {
  console.log('MOCK: Initiating login...');
  // Simulate redirect to Keycloak by adding query parameter and reloading
  const currentUrl = new URL(window.location.href);
  currentUrl.searchParams.set('mock_login', 'success');
  window.location.href = currentUrl.toString();
  return Promise.resolve();
};

export const doLogout = () => {
  console.log('MOCK: Logging out...');
  mockAuthenticated = false;
  mockToken = null;
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('mockToken');
  window.location.reload();
  return Promise.resolve();
};

export const getToken = () => {
  console.log('MOCK: Getting token:', mockToken ? 'Present' : 'Missing');
  return mockToken;
};

export const isAuthenticated = () => {
  const result = !!mockToken && mockAuthenticated;
  console.log('MOCK: Is authenticated:', result);
  return result;
};

export const isTokenExpired = () => {
  if (!mockToken) return true;
  
  // Decode the mock token to check expiration
  try {
    const payload = JSON.parse(atob(mockToken.split('.')[1]));
    const now = Math.floor(Date.now() / 1000);
    return now >= payload.exp;
  } catch (e) {
    return true;
  }
};

export const getUsername = () => {
  if (!mockToken) return null;
  return mockUser.preferred_username;
};

export const getUserRoles = () => {
  if (!mockToken) return [];
  return ['doctor', 'user'];
};

export const updateToken = (successCallback) => {
  console.log('MOCK: Refreshing token...');
  // Simulate token refresh
  if (mockAuthenticated) {
    mockToken = generateMockToken();
    localStorage.setItem('mockToken', mockToken);
    return Promise.resolve().then(() => {
      if (successCallback) successCallback();
    });
  } else {
    return Promise.reject(new Error('Not authenticated'));
  }
};

// Additional mock properties that might be accessed
export const tokenParsed = mockToken ? JSON.parse(atob(mockToken.split('.')[1])) : null;

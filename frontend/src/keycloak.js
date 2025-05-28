import Keycloak from 'keycloak-js';

const keycloakConfig = {
  url: (process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080') + '/auth',
  realm: process.env.REACT_APP_KEYCLOAK_REALM || 'datamed',
  clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'
};

const keycloak = new Keycloak(keycloakConfig);
let isInitialized = false;
let isInitializing = false;

export const initKeycloak = (onAuthenticatedCallback) => {
  if (isInitialized) {
    console.log('Keycloak already initialized, calling callback immediately');
    onAuthenticatedCallback();
    return;
  }
  
  if (isInitializing) {
    console.log('Keycloak initialization already in progress, ignoring duplicate call');
    return;
  }
  
  isInitializing = true;
  console.log('Starting Keycloak initialization...');
  console.log('Current URL:', window.location.href);
  
  // Check if we have authentication parameters in the URL
  const url = new URL(window.location.href);
  const hasAuthParams = url.searchParams.has('code') && url.searchParams.has('state');

  
  console.log('Has authentication parameters:', hasAuthParams);
  console.log('window.location.origin:', window.location.origin);
  console.log('window.location.href:', window.location.href);
  
  // Set a longer timeout when processing authentication parameters
  const timeoutDuration = hasAuthParams ? 20000 : 5000; // 20s for auth, 5s for normal check
  const timeoutId = setTimeout(() => {
    console.warn('Keycloak initialization timeout after', timeoutDuration/1000, 'seconds');
    isInitialized = true;
    isInitializing = false;
    onAuthenticatedCallback();
  }, timeoutDuration);

  // Different initialization strategy based on whether we have auth parameters
  const initOptions = hasAuthParams ? {
    // When we have auth parameters, process them directly
    onLoad: 'login-required',
    checkLoginIframe: false,
    pkceMethod: 'S256',
    redirectUri: window.location.origin,
    enableLogging: true,
    flow: 'standard',
  } : {
    // When no auth parameters, use silent SSO check
    onLoad: 'check-sso',
    silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
    pkceMethod: 'S256',
    checkLoginIframe: false,
    redirectUri: window.location.origin,
    enableLogging: true,
    flow: 'standard',
  };

  console.log('Initializing Keycloak with options:', initOptions);

  keycloak.init(initOptions)
  .then((authenticated) => {
    clearTimeout(timeoutId); // Clear the timeout since init succeeded
    isInitialized = true;
    isInitializing = false;
    console.log('Keycloak init success, authenticated:', authenticated);
    console.log('Token:', keycloak.token ? 'Present (length: ' + keycloak.token.length + ')' : 'Missing');
    console.log('Refresh token:', keycloak.refreshToken ? 'Present' : 'Missing');
    console.log('ID token:', keycloak.idToken ? 'Present' : 'Missing');
    console.log('Token parsed:', keycloak.tokenParsed ? 'Present' : 'Missing');
    console.log('Current URL after init:', window.location.href);
    
    if (authenticated && keycloak.token) {
      console.log('User authenticated successfully with token');
      localStorage.setItem('isAuthenticated', 'true');
      
      // Set cookie with proper expiration
      const expirationDate = new Date();
      expirationDate.setTime(expirationDate.getTime() + (24 * 60 * 60 * 1000)); // 24 hours
      document.cookie = `auth_token=${keycloak.token}; path=/; expires=${expirationDate.toUTCString()}`;
      
      // Clean URL after successful authentication - but only after we've processed the tokens
      const currentUrl = new URL(window.location.href);
      if (currentUrl.searchParams.has('session_code') || 
          currentUrl.searchParams.has('code') || 
          currentUrl.pathname.includes('login-actions')) {
        console.log('Cleaning authentication URL parameters...');
        window.history.replaceState({}, document.title, window.location.origin);
      }
      
      // Set up token refresh
      keycloak.onTokenExpired = () => {
        console.log('Token expired, refreshing...');
        keycloak.updateToken(70).catch(() => {
          console.log('Token refresh failed, redirecting to login');
          keycloak.login();
        });
      };
    } else {
      console.log('User not authenticated or token missing');
      console.log('Authenticated:', authenticated);
      console.log('Token present:', !!keycloak.token);
      localStorage.removeItem('isAuthenticated');
    }
    
    onAuthenticatedCallback();
  })
  .catch((error) => {
    clearTimeout(timeoutId); // Clear the timeout since we got a response
    isInitialized = true;
    isInitializing = false;
    console.error('Keycloak init failed:', error);
    console.error('Error type:', typeof error);
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    console.log('Current URL during error:', window.location.href);
    
    localStorage.removeItem('isAuthenticated');
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    onAuthenticatedCallback();
  });
};

export const doLogin = () => {
  console.log('Initiating login...');
  return keycloak.login({
    redirectUri: window.location.origin,
  });
};

export const doLogout = () => keycloak.logout();

export const getToken = () => keycloak.token;

export const isAuthenticated = () => !!keycloak.token;

export const isTokenExpired = () => keycloak.isTokenExpired();

export const getUsername = () => keycloak.tokenParsed?.preferred_username;

export const getUserRoles = () => {
  if (keycloak.tokenParsed && keycloak.tokenParsed.realm_access) {
    return keycloak.tokenParsed.realm_access.roles;
  }
  return [];
};

export const updateToken = (successCallback) => {
  return keycloak.updateToken(5)
    .then(successCallback)
    .catch(doLogin);
};
import Keycloak from 'keycloak-js';

const keycloakConfig = {
  url: (process.env.REACT_APP_KEYCLOAK_URL || 'https://localhost') + '/auth', // Use HTTPS and portless localhost for nginx proxy
  realm: process.env.REACT_APP_KEYCLOAK_REALM || 'datamed',
  clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'
};

const keycloak = new Keycloak(keycloakConfig);
let isInitialized = false;
let isInitializing = false;

export const initKeycloak = (onAuthenticatedCallback) => {
  if (isInitialized) {
    onAuthenticatedCallback();
    return;
  }
  
  if (isInitializing) {
    return;
  }
  
  isInitializing = true;
  const url = new URL(window.location.href);
  const hasAuthParams = url.searchParams.has('code') && url.searchParams.has('state');
  const timeoutDuration = hasAuthParams ? 20000 : 5000; 
  const timeoutId = setTimeout(() => {
    console.warn('Keycloak initialization timeout after', timeoutDuration/1000, 'seconds');
    isInitialized = true;
    isInitializing = false;
    onAuthenticatedCallback();
  }, timeoutDuration);


  const initOptions = hasAuthParams ? {
    onLoad: 'check-sso',
    checkLoginIframe: false,
    pkceMethod: 'S256',
    redirectUri: window.location.origin,
    enableLogging: true,
    flow: 'standard',
  } : {
    onLoad: 'check-sso',
    silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
    pkceMethod: 'S256',
    checkLoginIframe: false,
    redirectUri: window.location.origin,
    enableLogging: true,
    flow: 'standard',
  };

  keycloak.init(initOptions)
  .then((authenticated) => {
    clearTimeout(timeoutId); 
    isInitialized = true;
    isInitializing = false;
    if (authenticated && keycloak.token) {
      localStorage.setItem('isAuthenticated', 'true');
      const expirationDate = new Date();
      expirationDate.setTime(expirationDate.getTime() + (24 * 60 * 60 * 1000)); 
      document.cookie = `auth_token=${keycloak.token}; path=/; expires=${expirationDate.toUTCString()}`;
      
      const currentUrl = new URL(window.location.href);
      if (currentUrl.searchParams.has('session_code') || 
          currentUrl.searchParams.has('code') || 
          currentUrl.pathname.includes('login-actions')) {
        window.history.replaceState({}, document.title, window.location.origin);
      }
      keycloak.onTokenExpired = () => {
        keycloak.updateToken(70).catch(() => {
          keycloak.login();
        });
      };
    } else {
      localStorage.removeItem('isAuthenticated');
    }
    
    onAuthenticatedCallback();
  })
  .catch((error) => {
    clearTimeout(timeoutId); 
    isInitialized = true;
    isInitializing = false;    
    localStorage.removeItem('isAuthenticated');
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    onAuthenticatedCallback();
  });
};

export const doLogin = () => {
  return keycloak.login({
    redirectUri: window.location.origin,
    scope: 'openid profile email'
  });
};

export const doLogout = async (navigate) => {
  try {
    const token = getToken();
    if (token) {
      await fetch(`${process.env.REACT_APP_API_URL || 'https://localhost/api'}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      }).catch(err => console.log('Backend logout call failed:', err));
    }
  } catch (error) {
  }
  localStorage.removeItem('isAuthenticated');
  document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
  if (navigate) {
    navigate('/');
    return;
  }
  return keycloak.logout({
    redirectUri: window.location.origin
  });
};

export const getToken = () => keycloak.token;

export const isAuthenticated = () => {
  const hasToken = !!keycloak.token;
  const localStorageAuth = localStorage.getItem('isAuthenticated') === 'true';
  console.log('isAuthenticated check - hasToken:', hasToken, 'localStorage:', localStorageAuth, 'keycloak.authenticated:', keycloak.authenticated);
  return hasToken && !keycloak.isTokenExpired();
};

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
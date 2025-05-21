import Keycloak from 'keycloak-js';
const keycloakConfig = {
  url: (process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080') + '/auth',
  realm: process.env.REACT_APP_KEYCLOAK_REALM || 'datamed',
  clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'
};

const keycloak = new Keycloak(keycloakConfig);

export const initKeycloak = (onAuthenticatedCallback) => {
  keycloak.init({
    onLoad: 'check-sso',
    silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
    pkceMethod: 'S256'
  })
    .then((authenticated) => {
      if (authenticated) {
        console.log('User is authenticated');
        document.cookie = `auth_token=${keycloak.token}; path=/`;
      } else {
        console.log('User is not authenticated');
      }
      onAuthenticatedCallback();
    })
    .catch(error => {
      console.error('Failed to initialize Keycloak', error);
      onAuthenticatedCallback();
    });
};

export const doLogin = () => keycloak.login();

export const doLogout = () => keycloak.logout();

export const getToken = () => keycloak.token;

export const isAuthenticated = () => !!keycloak.token;

export const isTokenExpired = () => keycloak.isTokenExpired();

export const updateToken = (successCallback) => {
  return keycloak.updateToken(5)
    .then(successCallback)
    .catch(doLogin);
};

export const getUsername = () => keycloak.tokenParsed?.preferred_username;

export const getUserRoles = () => {
  if (keycloak.tokenParsed && keycloak.tokenParsed.realm_access) {
    return keycloak.tokenParsed.realm_access.roles;
  }
  return [];
};

export const hasRole = (roles) => {
  return roles.some(role => {
    const userRoles = getUserRoles();
    return userRoles.includes(role);
  });
};

export default keycloak;

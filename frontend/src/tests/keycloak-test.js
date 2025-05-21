import { initKeycloak, isAuthenticated, getToken } from '../keycloak';

export const testKeycloakInit = () => {
  console.log('Starting Keycloak initialization test...');

  const keycloakUrl = process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080';
  console.log(`Using Keycloak URL: ${keycloakUrl}/auth`);

  console.log('Testing network connectivity to Keycloak server...');
  fetch(`${keycloakUrl}/auth`)
    .then(response => {
      console.log(`Keycloak server response status: ${response.status}`);
      if (!response.ok) {
        console.error('Failed to connect to Keycloak server');
      } else {
        console.log('Successfully connected to Keycloak server');
      }
    })
    .catch(error => {
      console.error('Network error when connecting to Keycloak server:', error);
    });

  // Test Keycloak initialization with timeout
  console.log('Testing Keycloak initialization...');
  const initTimeout = setTimeout(() => {
    console.error('Keycloak initialization timed out after 10 seconds');
  }, 10000);

  initKeycloak((authenticated) => {
    clearTimeout(initTimeout);
    console.log('Keycloak initialization completed');
    console.log(`Authenticated: ${isAuthenticated()}`);
    console.log(`Token available: ${!!getToken()}`);

    if (isAuthenticated()) {
      console.log('User is authenticated, token is available');
    } else {
      console.log('User is not authenticated, no token available');
    }
  });
};

export const monitorKeycloakRequests = () => {
  const originalFetch = window.fetch;

  window.fetch = function(url, options) {
    const startTime = performance.now();
    console.log(`Fetch request to: ${url}`, options);

    return originalFetch.apply(this, arguments)
      .then(response => {
        const endTime = performance.now();
        console.log(`Fetch response from: ${url}`, {
          status: response.status,
          ok: response.ok,
          time: endTime - startTime
        });
        return response;
      })
      .catch(error => {
        console.error(`Fetch error for: ${url}`, error);
        throw error;
      });
  };

  console.log('Network request monitoring enabled');
};

export const checkSilentCheckSso = () => {
  console.log('Checking if silent-check-sso.html is accessible...');
  fetch(`${window.location.origin}/silent-check-sso.html`)
    .then(response => {
      console.log(`silent-check-sso.html response status: ${response.status}`);
      if (!response.ok) {
        console.error('silent-check-sso.html is not accessible');
      } else {
        console.log('silent-check-sso.html is accessible');
      }
    })
    .catch(error => {
      console.error('Error accessing silent-check-sso.html:', error);
    });
};

export const testCorsIssues = () => {
  console.log('Testing for CORS issues...');

  const keycloakUrl = process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080';
  const realm = process.env.REACT_APP_KEYCLOAK_REALM || 'datamed';
  const clientId = process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client';

  const endpoints = [
    `/auth/realms/${realm}`,
    `/auth/realms/${realm}/protocol/openid-connect/auth`,
    `/auth/realms/${realm}/protocol/openid-connect/token`
  ];

  endpoints.forEach(endpoint => {
    const url = `${keycloakUrl}${endpoint}`;
    console.log(`Testing CORS for: ${url}`);

    fetch(url, {
      method: 'OPTIONS',
      headers: {
        'Origin': window.location.origin,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Authorization'
      }
    })
    .then(response => {
      console.log(`CORS preflight response for ${endpoint}:`, {
        status: response.status,
        ok: response.ok,
        headers: {
          'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
          'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
          'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
      });

      if (response.headers.get('Access-Control-Allow-Origin') !== window.location.origin && 
          response.headers.get('Access-Control-Allow-Origin') !== '*') {
        console.error(`CORS issue detected: ${endpoint} does not allow origin ${window.location.origin}`);
      }
    })
    .catch(error => {
      console.error(`CORS test error for ${endpoint}:`, error);
    });
  });
};

export const checkKeycloakConfig = () => {
  console.log('Checking Keycloak configuration...');

  const keycloakUrl = process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080';
  const realm = process.env.REACT_APP_KEYCLOAK_REALM || 'datamed';
  const clientId = process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client';

  console.log('Current Keycloak configuration:', {
    url: keycloakUrl + '/auth',
    realm,
    clientId
  });

  fetch(`${keycloakUrl}/auth/realms/${realm}`)
    .then(response => {
      if (response.ok) {
        console.log(`Realm '${realm}' exists`);
        return response.json();
      } else {
        console.error(`Realm '${realm}' does not exist or is not accessible`);
        throw new Error(`Realm '${realm}' not found`);
      }
    })
    .then(realmInfo => {
      console.log('Realm information:', realmInfo);
    })
    .catch(error => {
      console.error('Error checking realm:', error);
    });
};

export const runAllTests = () => {
  console.log('Running all Keycloak tests...');
  monitorKeycloakRequests();
  checkSilentCheckSso();
  checkKeycloakConfig();
  testCorsIssues();
  testKeycloakInit();
};

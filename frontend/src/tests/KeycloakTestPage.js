import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  runAllTests, 
  testKeycloakInit, 
  monitorKeycloakRequests, 
  checkSilentCheckSso,
  testCorsIssues,
  checkKeycloakConfig
} from './keycloak-test';
import './KeycloakTestPage.css';

function KeycloakTestPage() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const [testRunning, setTestRunning] = useState(false);

  useEffect(() => {
    const originalConsoleLog = console.log;
    const originalConsoleError = console.error;

    console.log = (...args) => {
      originalConsoleLog(...args);
      setLogs(prevLogs => [...prevLogs, { type: 'log', message: args.join(' ') }]);
    };

    console.error = (...args) => {
      originalConsoleError(...args);
      setLogs(prevLogs => [...prevLogs, { type: 'error', message: args.join(' ') }]);
    };

    return () => {
      console.log = originalConsoleLog;
      console.error = originalConsoleError;
    };
  }, []);

  const handleRunAllTests = () => {
    setLogs([]);
    setTestRunning(true);
    setTimeout(() => {
      runAllTests();
      setTestRunning(false);
    }, 100);
  };

  const handleTestKeycloakInit = () => {
    setLogs([]);
    setTestRunning(true);
    setTimeout(() => {
      testKeycloakInit();
      setTestRunning(false);
    }, 100);
  };

  const handleMonitorRequests = () => {
    setLogs([]);
    monitorKeycloakRequests();
  };

  const handleCheckSilentSso = () => {
    setLogs([]);
    checkSilentCheckSso();
  };

  const handleTestCorsIssues = () => {
    setLogs([]);
    testCorsIssues();
  };

  const handleCheckKeycloakConfig = () => {
    setLogs([]);
    checkKeycloakConfig();
  };

  const handleClearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="keycloak-test-page">
      <div className="header">
        <h1>Keycloak Connection Test</h1>
        <div className="header-buttons">
          <button onClick={() => navigate("/")} className="nav-button">
            Back to Login
          </button>
        </div>
      </div>

      <div className="test-controls">
        <button onClick={handleRunAllTests} disabled={testRunning}>
          Run All Tests
        </button>
        <button onClick={handleTestKeycloakInit} disabled={testRunning}>
          Test Keycloak Init
        </button>
        <button onClick={handleMonitorRequests}>
          Monitor Network Requests
        </button>
        <button onClick={handleCheckSilentSso}>
          Check Silent-Check-SSO
        </button>
        <button onClick={handleTestCorsIssues}>
          Test CORS Issues
        </button>
        <button onClick={handleCheckKeycloakConfig}>
          Check Keycloak Config
        </button>
        <button onClick={handleClearLogs}>
          Clear Logs
        </button>
      </div>

      <div className="test-logs">
        <h2>Test Logs</h2>
        {testRunning && <div className="loading">Tests running...</div>}
        <div className="logs-container">
          {logs.map((log, index) => (
            <div key={index} className={`log-entry ${log.type}`}>
              {log.message}
            </div>
          ))}
          {logs.length === 0 && <div className="no-logs">No logs yet. Run a test to see results.</div>}
        </div>
      </div>

      <div className="test-info">
        <h2>Troubleshooting Information</h2>
        <p>This page helps diagnose issues with Keycloak authentication:</p>
        <ul>
          <li><strong>Run All Tests</strong> - Runs all Keycloak connection tests</li>
          <li><strong>Test Keycloak Init</strong> - Tests only the Keycloak initialization</li>
          <li><strong>Monitor Network Requests</strong> - Monitors all network requests</li>
          <li><strong>Check Silent-Check-SSO</strong> - Verifies the silent-check-sso.html file</li>
          <li><strong>Test CORS Issues</strong> - Checks for CORS configuration problems</li>
          <li><strong>Check Keycloak Config</strong> - Verifies Keycloak realm and client configuration</li>
        </ul>
        <p>Common issues:</p>
        <ul>
          <li>Keycloak server not running or inaccessible</li>
          <li>Missing or incorrect silent-check-sso.html file</li>
          <li>CORS issues preventing communication between frontend and Keycloak</li>
          <li>Incorrect Keycloak configuration (URL, realm, client)</li>
          <li>Network connectivity problems or firewall restrictions</li>
          <li>Keycloak realm or client not properly configured</li>
        </ul>
        <p>How to fix common issues:</p>
        <ul>
          <li>Ensure Keycloak server is running and accessible at the configured URL</li>
          <li>Verify that silent-check-sso.html exists in the public directory</li>
          <li>Check that CORS is properly configured in Keycloak for your frontend origin</li>
          <li>Confirm that the realm and client ID match what's configured in Keycloak</li>
          <li>Check browser console for any JavaScript errors during initialization</li>
          <li>Verify network requests in browser developer tools for any failed requests</li>
        </ul>
      </div>

    </div>
  );
}

export default KeycloakTestPage;

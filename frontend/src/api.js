/**
 * API client for Instagram Compatibility backend
 */

const API_BASE = '/api';

/**
 * Create a new matching session
 */
export async function createSession() {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Failed to create session');
  }
  
  return response.json();
}

/**
 * Get session status
 */
export async function getSessionStatus(sessionCode) {
  const response = await fetch(`${API_BASE}/sessions/${sessionCode}`);
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Session not found or expired');
    }
    throw new Error('Failed to get session status');
  }
  
  return response.json();
}

/**
 * Upload Instagram data export
 */
export async function uploadData(sessionCode, file, person) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('person', person);
  
  const response = await fetch(`${API_BASE}/sessions/${sessionCode}/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload data');
  }
  
  return response.json();
}

/**
 * Get compatibility result
 */
export async function getResult(sessionCode) {
  const response = await fetch(`${API_BASE}/sessions/${sessionCode}/result`);
  
  if (!response.ok) {
    if (response.status === 400) {
      throw new Error('Result not ready yet');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get result');
  }
  
  return response.json();
}

/**
 * Get privacy info
 */
export async function getPrivacyInfo() {
  const response = await fetch(`${API_BASE}/privacy-info`);
  
  if (!response.ok) {
    throw new Error('Failed to get privacy info');
  }
  
  return response.json();
}

/**
 * Delete session
 */
export async function deleteSession(sessionCode) {
  const response = await fetch(`${API_BASE}/sessions/${sessionCode}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete session');
  }
  
  return response.json();
}

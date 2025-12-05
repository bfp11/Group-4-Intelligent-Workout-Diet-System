/**
 * API Service for connecting to the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Helper function to handle API responses
 */
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || error.message || 'Something went wrong');
  }
  return response.json();
}

/**
 * Generate a personalized workout and meal plan
 */
export async function generatePlan(userData) {
  const response = await fetch(`${API_BASE_URL}/generate-plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return handleResponse(response);
}

// Export other functions...
export default {
  generatePlan,
};
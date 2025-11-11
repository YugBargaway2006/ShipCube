import axios from 'axios';

// 1. Create a pre-configured Axios instance
// The 'baseURL' should point to your backend.
// Update 'http://localhost:8000' to your actual backend server address.
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // Assumes backend is at port 8000 and has a /api prefix
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

/**
 * 2. A robust error handler for all API calls.
 * This normalizes complex Axios errors into a simple, consumable object.
 */
const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx [24]
    console.error('API Error Response:', error.response.data);
    return {
      status: error.response.status,
      message: error.response.data.message || `Server error: ${error.response.status}`,
    };
  } else if (error.request) {
    // The request was made but no response was received [25]
    console.error('API Error Request:', error.request);
    return {
      status: null,
      message: 'Network error: The server did not respond.',
    };
  } else {
    // Something happened in setting up the request that triggered an Error
    console.error('API Error Message:', error.message);
    return {
      status: null,
      message: error.message,
    };
  }
};

/**
 * 3. Exported function for the /chat/query (NER) endpoint
 * Uses async/await syntax [9, 10]
 */
export const postQuery = async (text) => {
  try {
    const response = await apiClient.post('/chat/query', {
      text: text,
      // In a stateful app, you might also send a sessionId
    });
    // Axios wraps the response data in a 'data' object
    return response.data;
  } catch (error) {
    // Pass the error to our normalizer and re-throw
    throw handleApiError(error);
  }
};

/**
 * 4. Exported function for the /process/email endpoint
 */
export const postEmailAction = async (action, payload) => {
  try {
    const response = await apiClient.post('/process/email', {
      action: action,
      payload: payload,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};
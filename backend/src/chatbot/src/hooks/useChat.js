import { useState } from 'react';
import * as apiService from '../services/apiService';

// Custom hook to manage all chat state and logic
export const useChat = () => {
  const [messages, setMessages] = useState([]);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Generates a unique ID for messages.
   * In a production app, this might come from a library like 'uuid'.
   */
  const generateId = () => `msg_${new Date().getTime()}`;

  /**
   * Handles sending a query to the /chat/query (NER) endpoint.
   */
  const sendMessage = async (text) => {
    // 1. Optimistic UI update for the user's message
    const userMessage = {
      id: generateId(),
      user: 'human',
      text: text,
    };
    setMessages(prev => [...prev, userMessage]);

    // 2. Set loading state and clear previous errors
    setIsLoading(true);
    setError(null);

    try {
      // 3. Call the API service
      const responseData = await apiService.postQuery(text);

      // 4. Handle success: Add the AI's response
      const aiMessage = {
        id: generateId(),
        user: 'ai',
       ...responseData, // Spread the response (responseText, entities)
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {
      // 5. Handle failure: Set the error state
      setError(err);
      
      // Optionally add an error message to the chat
      const errorMessage = {
        id: generateId(),
        user: 'ai',
        responseText: `Sorry, I encountered an error: ${err.message}`,
        entities: [],
      };
      setMessages(prev => [...prev, errorMessage]);

    } finally {
      // 6. Cleanup: Stop loading
      setIsLoading(false);
    }
  };

  /**
   * Handles sending an action to the /process/email endpoint.
   * This is called from the ComposeEmailModal.
   */
  const sendEmailAction = async (action, payload) => {
    // 1. Set loading state and clear errors
    setIsLoading(true);
    setError(null);
    
    // Add a message to the UI to show work is in progress
    const thinkingMessage = {
      id: generateId(),
      user: 'ai',
      responseText: `Drafting your email to ${payload.to}...`,
      entities: [],
    };
    setMessages(prev => [...prev, thinkingMessage]);

    try {
      // 2. Call the API service
      const responseData = await apiService.postEmailAction(action, payload);

      // 3. Handle success: Add the AI's confirmation message
      const successMessage = {
        id: generateId(),
        user: 'ai',
        responseText: responseData.data?.summary || 'Email action completed.',
        entities: [],
      };
      setMessages(prev => [...prev, successMessage]);

      return responseData; // Return data to modal if needed (e.g., to close it)

    } catch (err) {
      // 4. Handle failure
      setError(err);
      const errorMessage = {
        id: generateId(),
        user: 'ai',
        responseText: `Failed to process email action: ${err.message}`,
        entities: [],
      };
      setMessages(prev => [...prev, errorMessage]);

      throw err; // Re-throw error to modal if needed

    } finally {
      // 5. Cleanup
      setIsLoading(false);
    }
  };

  // Expose state and handlers to the components
  return {
    messages,
    isLoading,
    error,
    sendMessage,
    sendEmailAction,
  };
};
import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

export const ChatContainer = ({ messages, isLoading, error, onSend }) => {
  return (
    <div className="chat-container">
      <MessageList 
        messages={messages} 
        isLoading={isLoading} 
      />
      
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error.message || 'An unknown error occurred.'}
        </div>
      )}
      
      <ChatInput onSend={onSend} disabled={isLoading} />
    </div>
  );
};
import React, { useRef, useEffect } from 'react';
import { Message } from './Message';
import { Loader } from './Loader';

export const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom when messages array changes
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <div className="message-list">
      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}
      
      {isLoading && <Loader />}
      
      {/* Empty div to act as a scroll target */}
      <div ref={messagesEndRef} />
    </div>
  );
};
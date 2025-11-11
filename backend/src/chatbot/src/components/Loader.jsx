import React from 'react';

export const Loader = () => {
  return (
    <div className="message ai">
      <div className="message-bubble loader-bubble">
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};
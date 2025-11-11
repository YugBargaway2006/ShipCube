import React from 'react';
import { MessageRenderer } from './MessageRenderer';

export const Message = ({ message }) => {
  const isHuman = message.user === 'human';
  const messageClass = isHuman? 'message human' : 'message ai';

  return (
    <div className={messageClass}>
      <div className="message-bubble">
        {/* 
          We pass the message to MessageRenderer.
          If it's a simple text message, it will render text.
          If it has NER entities, it will render highlighted text.
        */}
        <MessageRenderer message={message} />
      </div>
    </div>
  );
};
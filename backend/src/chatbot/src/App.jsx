import React, { useState } from 'react';
import { ChatContainer } from './components/ChatContainer';
import { ComposeEmailModal } from './components/ComposeEmailModal';
import { useChat } from './hooks/useChat';
import './index.css';

function App() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    sendEmailAction,
  } = useChat();
  
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <h1>AI Email Agent</h1>
        <button 
          onClick={() => setIsModalOpen(true)} 
          className="header-button"
        >
          Compose Email
        </button>
      </header>
      
      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        error={error}
        onSend={sendMessage}
      />
      
      <ComposeEmailModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSendEmail={sendEmailAction}
      />
    </div>
  );
}

export default App;
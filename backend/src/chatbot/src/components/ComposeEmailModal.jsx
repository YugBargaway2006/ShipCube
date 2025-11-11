import React, { useState } from 'react';

export const ComposeEmailModal = ({ isOpen, onClose, onSendEmail }) => {
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSending(true);
    setError(null);

    const payload = { to, subject, body };

    try {
      // Call the useChat hook's sendEmailAction function
      await onSendEmail('send_email', payload);
      
      // Success: clear form and close modal
      setTo('');
      setSubject('');
      setBody('');
      onClose();
      
    } catch (err) {
      setError(err.message || 'Failed to send email draft.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Compose AI Draft</h2>
          <button onClick={onClose} className="modal-close-button">&times;</button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="to">To:</label>
              <input
                id="to"
                type="email"
                value={to}
                onChange={(e) => setTo(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="subject">Subject:</label>
              <input
                id="subject"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="body">Body (AI will refine this):</label>
              <textarea
                id="body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                required
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}

            <div className="modal-footer">
              <button 
                type="button" 
                className="modal-button cancel" 
                onClick={onClose}
                disabled={isSending}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="modal-button send"
                disabled={isSending}
              >
                {isSending? 'Sending...' : 'Send Draft'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
import { useState, useRef } from 'react';
import { FaPaperclip, FaPaperPlane } from 'react-icons/fa';
import axios from 'axios';

const Chat = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  // Add these at the top of your Chat component
  const [uploadStatus, setUploadStatus] = useState(null); // 'success', 'error', or null
  const [uploadMessage, setUploadMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/generate', {
        prompt: input
      });
      
      setMessages(prev => [...prev, 
        { text: input, isUser: true },
        { 
          text: response.data.response,
          isUser: false,
          meta: {
            source: response.data.source,  // Should be "cache", "llm", or "llm+docs"
            docsUsed: response.data.docs_used || 0  // Changed from relevant_docs
          }
        }
      ]);
      setInput('');
    } catch (error) {
      console.error(error);
    }
    setIsLoading(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);
    setIsUploading(true);
    setUploadStatus(null);
    setUploadMessage('');
  
    const formData = new FormData();
    formData.append('file', file);
  
    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadStatus('success');
      setUploadMessage(response.data.message || 'File uploaded successfully!');
    } catch (error) {
      setUploadStatus('error');
      setUploadMessage(error.response?.data?.error || 'File upload failed');
    } finally {
      setIsUploading(false);
      // Clear status after 3 seconds
      setTimeout(() => {
        setUploadStatus(null);
        setUploadMessage('');
      }, 3000);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
      
        {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.isUser ? 'user' : 'ai'}`}>
            {msg.text}
            {!msg.isUser && msg.meta?.source && (
            <div className="response-source">
                {msg.meta.source === "llm+docs" && "Generated from document content"}
            </div>
            )}
        </div>
        ))}
        
        {isLoading && <div className="loading-animation">...</div>}
      </div>
      <div className="upload-status-container">
  {isUploading && (
    <div className="upload-loading">
      <div className="spinner"></div>
      Uploading...
    </div>
  )}
  {uploadStatus && (
    <div className={`status-message ${uploadStatus}`}>
      {uploadMessage}
    </div>
  )}
    </div>
      <form onSubmit={handleSubmit} className="input-area">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf"
          hidden
        />
        {fileName && (
  <div className="file-name">
    {fileName}
    <button 
      type="button" 
      className="clear-file"
      onClick={() => {
        setFileName('');
        fileInputRef.current.value = '';
      }}
    >
      ×
    </button>
  </div>
)}
        <button
          type="button"
          className="upload-btn"
          onClick={() => fileInputRef.current.click()}
        >
          <FaPaperclip />
        </button>
        
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your query..."
        />
        
        <button type="submit" className="send-btn">
          <FaPaperPlane />
        </button>
      </form>
    </div>
  );
};

export default Chat;
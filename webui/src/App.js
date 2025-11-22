import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

// Generate or reuse a persistent session ID for this browser
const getOrCreateSessionId = () => {
  let id = localStorage.getItem("gift_agent_session_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("gift_agent_session_id", id);
  }
  return id;
};

const SESSION_ID = getOrCreateSessionId();
const API_URL = "/chat"; // relative path for Cloud Run

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [message]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage("");

    // Add user message to chat
    setMessages(prev => [...prev, { type: "user", content: userMessage }]);

    setLoading(true);
    try {
      const res = await axios.post(API_URL, {
        message: userMessage,
        session_id: SESSION_ID,
      });

      // Add assistant response to chat
      setMessages(prev => [...prev, { type: "assistant", content: res.data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        type: "assistant",
        content: "⚠️ Error: " + err.message
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setMessage(suggestion);
    textareaRef.current?.focus();
  };

  const suggestions = [
    "Help me find a gift for my sister who loves art",
    "What's a good gift for a tech enthusiast?",
    "I need gift ideas for my mom's birthday",
  ];

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <span className="app-icon">🎁</span>
          <h1 className="app-title">Gift Planning Assistant</h1>
          <div className="app-subtitle">
            <span className="status-indicator"></span>
            <span>Online</span>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="chat-container">
        <div className="messages-area">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🎁</div>
              <h2 className="empty-title">Welcome to Gift Planning Assistant</h2>
              <p className="empty-description">
                I'm here to help you find the perfect gifts for your loved ones.
                Tell me about the person you're shopping for, and I'll suggest thoughtful gift ideas.
              </p>
              <div className="suggestions">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.type}`}>
                  <div className="message-avatar">
                    {msg.type === "user" ? (
                      <div className="avatar-circle user-avatar">U</div>
                    ) : (
                      <div className="avatar-circle assistant-avatar">🎁</div>
                    )}
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-avatar">
                    <div className="avatar-circle assistant-avatar">🎁</div>
                  </div>
                  <div className="loading-message">
                    <div className="loading-dots">
                      <span className="loading-dot"></span>
                      <span className="loading-dot"></span>
                      <span className="loading-dot"></span>
                    </div>
                    <span style={{ fontSize: '13px', color: 'var(--text-tertiary)' }}>
                      Thinking...
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div className="input-wrapper">
            <div className="textarea-wrapper">
              <textarea
                ref={textareaRef}
                className="chat-input"
                placeholder="Ask me anything about gift planning..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
              />
            </div>
            <div className="input-actions">
              <div className="input-hint">
                <span>Press</span>
                <kbd className="kbd">Enter</kbd>
                <span>to send</span>
              </div>
              <button
                className="send-button"
                onClick={sendMessage}
                disabled={loading || !message.trim()}
              >
                <span>{loading ? "Sending..." : "Send"}</span>
                <span className="button-icon">→</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p className="footer-text">
            <span>Crafted with</span>
            <span className="footer-heart">❤️</span>
            <span>by</span>
            <span className="footer-name">Akshay Kumar</span>
          </p>
          <div className="footer-divider"></div>
          <div className="social-links">
            <a
              href="https://www.linkedin.com/in/akshaykumar0611/"
              target="_blank"
              rel="noopener noreferrer"
              className="social-link linkedin"
              aria-label="LinkedIn Profile"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
            </a>
            <a
              href="https://github.com/akshay0611"
              target="_blank"
              rel="noopener noreferrer"
              className="social-link github"
              aria-label="GitHub Profile"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

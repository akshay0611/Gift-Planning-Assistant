import React, { useState } from "react";
import axios from "axios";

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
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message) return;

    setLoading(true);
    try {
      const res = await axios.post(API_URL, {
        message,
        session_id: SESSION_ID, // 🔥 attach session ID
      });

      setReply(res.data.reply);
    } catch (err) {
      setReply("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "50px auto", fontFamily: "sans-serif" }}>
      <h1>🎁 Gift Planning Assistant</h1>

      <textarea
        rows={4}
        style={{ width: "100%", marginTop: "20px" }}
        placeholder="Ask anything..."
        value={message}
        onChange={e => setMessage(e.target.value)}
      ></textarea>

      <button 
        onClick={sendMessage} 
        disabled={loading}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          background: "#333",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer"
        }}
      >
        {loading ? "Thinking..." : "Send"}
      </button>

      {reply && (
        <div style={{ marginTop: "30px", padding: "20px", background: "#f1f1f1", borderRadius: "6px" }}>
          <strong>Assistant:</strong>
          <p>{reply}</p>
        </div>
      )}
    </div>
  );
}

export default App;

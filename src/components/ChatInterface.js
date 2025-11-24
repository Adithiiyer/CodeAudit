import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  Typography,
  Box,
  CircularProgress
} from '@mui/material';

function ChatInterface({ submissionId }) {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    startChatSession();
  }, [submissionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startChatSession = async () => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/v1/chat/start`,
        null,
        { params: { submission_id: submissionId } }
      );
      setSessionId(response.data.session_id);
      
      // Add welcome message
      setMessages([{
        role: 'assistant',
        content: 'Hi! I can help you understand your code review. Ask me anything about the issues found, scores, or how to improve your code.'
      }]);
    } catch (error) {
      console.error('Error starting chat:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    const userMessage = inputMessage;
    setInputMessage('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/v1/chat/${sessionId}/message`,
        null,
        { params: { message: userMessage } }
      );

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.assistant_response
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <Paper sx={{ p: 3, height: '600px', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>
        Ask Questions About Your Review
      </Typography>

      {/* Messages Area */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <List>
          {messages.map((msg, idx) => (
            <ListItem
              key={idx}
              sx={{
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 1
              }}
            >
              <Paper
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: msg.role === 'user' ? 'primary.light' : 'white',
                  color: msg.role === 'user' ? 'white' : 'text.primary'
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </Typography>
              </Paper>
            </ListItem>
          ))}
          {loading && (
            <ListItem sx={{ justifyContent: 'flex-start' }}>
              <CircularProgress size={24} />
            </ListItem>
          )}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about your code review..."
          disabled={loading || !sessionId}
        />
        <Button
          variant="contained"
          onClick={sendMessage}
          disabled={loading || !inputMessage.trim() || !sessionId}
        >
          Send
        </Button>
      </Box>

      {/* Suggested Questions */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="textSecondary">
          Try asking:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
          {[
            "Why did this get a low score?",
            "How do I fix the security issues?",
            "What's wrong with line 42?",
            "Can you explain the complexity warning?"
          ].map((suggestion, idx) => (
            <Button
              key={idx}
              size="small"
              variant="outlined"
              onClick={() => setInputMessage(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </Box>
      </Box>
    </Paper>
  );
}

export default ChatInterface;
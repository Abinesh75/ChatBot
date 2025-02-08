import React, { useState } from "react";
import axios from "axios";
import {
  Container, TextField, Button, Typography, Paper, List, ListItem, ListItemText,
  Box, CircularProgress, AppBar, Toolbar, IconButton
} from "@mui/material";

const App = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChat = async () => {
    if (!query) return;
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:5000/chat", { query });
      setResponse(res.data.response);
      setHistory([...history, { query, response: res.data.response }]);
    } catch (error) {
      console.error("Error fetching response:", error);
      setResponse("⚠️ Error connecting to chatbot.");
    }

    setLoading(false);
  };

  return (
    <Box
      sx={{
        width: "100vw",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(to right, #141e30, #243b55)",
      }}
    >
      <Paper
        elevation={5}
        sx={{
          width: "500px",
          padding: 3,
          textAlign: "center",
          backgroundColor: "#1e1e1e",
          color: "#fff",
          borderRadius: 3,
        }}
      >
        <AppBar
          position="static"
          sx={{
            background: "linear-gradient(to right, #6a11cb, #2575fc)",
            borderRadius: 2,
          }}
        >
          <Toolbar sx={{ justifyContent: "center" }}>
            <IconButton color="inherit">
              💬 {/* Replaced ChatIcon with emoji */}
            </IconButton>
            <Typography variant="h6">AI Chatbot</Typography>
          </Toolbar>
        </AppBar>

        <TextField
          fullWidth
          variant="outlined"
          label="Ask me anything..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{ marginTop: 2, backgroundColor: "#fff", borderRadius: 1 }}
        />

        <Button
          variant="contained"
          color="secondary"
          fullWidth
          onClick={handleChat}
          sx={{ marginTop: 2, background: "linear-gradient(to right, #8e2de2, #4a00e0)" }}
        >
          Send 📩 {/* Replaced SendIcon with emoji */}
        </Button>

        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", marginTop: 2 }}>
            <CircularProgress color="secondary" />
          </Box>
        )}

        {!loading && response && (
          <Box
            sx={{
              marginTop: 2,
              padding: 2,
              backgroundColor: "#222",
              color: "#fff",
              borderRadius: 2,
            }}
          >
            <Typography variant="h6">🤖 AI Response:</Typography>
            <Typography>{response}</Typography>
          </Box>
        )}

        {history.length > 0 && (
          <Paper
            sx={{
              marginTop: 2,
              padding: 2,
              maxHeight: "200px",
              overflowY: "auto",
              backgroundColor: "#2e2e2e",
              color: "#fff",
              borderRadius: 2,
            }}
          >
            <Typography variant="h6">📝 Chat History:</Typography>
            <List>
              {history.map((entry, index) => (
                <ListItem key={index} sx={{ borderBottom: "1px solid #444" }}>
                  <ListItemText primary={`🗣️ ${entry.query}`} secondary={`🤖 ${entry.response}`} />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}
      </Paper>
    </Box>
  );
};

export default App;


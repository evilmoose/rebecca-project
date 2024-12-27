import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: { 
    messages: [],
    isStreaming: false, 
  },
    
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    updateLastMessage: (state, action) => {
      const currentMessage = state.messages[state.messages.length - 1];
      const newContent = action.payload;
  
      if (currentMessage.role === "assistant") {
          // Only update the last message content
          state.messages[state.messages.length - 1].content = newContent;
      } else {
          // Append a new assistant message
          state.messages.push({
              role: "assistant",
              content: newContent,
              name: "Rebecca",
          });
      }
  },
    setStreaming: (state, action) => {
      state.isStreaming = action.payload;
    }
  },
});

export const { addMessage, updateLastMessage, setStreaming } = chatSlice.actions;
export default chatSlice.reducer;
import { createSlice } from '@reduxjs/toolkit';

const userSlice = createSlice({
  name: 'user',
  initialState: {
    username: localStorage.getItem('username') || 'User',
    token: localStorage.getItem('token') || '',
  },
  reducers: {
    setUser: (state, action) => {
      state.username = action.payload.username;
      state.token = action.payload.token;
      localStorage.setItem('username', action.payload.username);
      localStorage.setItem('token', action.payload.token);
    },
    clearUser: (state) => {
      state.username = '';
      state.token = '';
      localStorage.removeItem('username');
      localStorage.removeItem('token');
    },
  },
});

export const { setUser, clearUser } = userSlice.actions;
export default userSlice.reducer;

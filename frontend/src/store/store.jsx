import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './chatSlice';
import userReducer from './usersSlice';
import authReducer from './authSlice';

const store = configureStore({
  reducer: {
    chat: chatReducer,
    user: userReducer,
    auth: authReducer,
  },
});

export default store;

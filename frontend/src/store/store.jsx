import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './slices/chatSlice';
import userReducer from './slices/usersSlice';
import authReducer from './slices/authSlice';
import pixijsReducer from './slices/pixijsSlice';

const store = configureStore({
  reducer: {
    chat: chatReducer,
    user: userReducer,
    auth: authReducer,
    pixijs: pixijsReducer,
  },
});

export default store;

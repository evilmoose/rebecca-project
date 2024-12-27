// eslint-disable-next-line no-unused-vars
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Home from './pages/Home';
import './App.css';
import './bootstrap.css';

const App = () => {
  //const [count, setCount] = useState(0)
  //const dispatch = useDispatch();
  //const conversations = useSelector((state) => state.chat.conversations);
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <Router>
      <Routes>
      <Route path="/" element={isAuthenticated ? <Home /> : <Navigate to="/login" />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/chat"
        element={isAuthenticated ? <Chat /> : <Navigate to="/login" />}
      />
      </Routes>
    </Router>
  );
};

export default App;

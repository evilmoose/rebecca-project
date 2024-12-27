// eslint-disable-next-line no-unused-vars
import React from 'react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return(
    <header className="d-flex align-items-center px-3 py-2 border-bottom">
      <h2 className="me-auto">Rebecca</h2>
      <button id="dark-mode-toggle" className="btn btn-secondary me-2">Toggle Dark Mode</button>
      <button id="logout-button" className="btn btn-outline-danger" onClick={handleLogout}>Logout</button>
      <button 
        className="btn btn-outline-primary" 
        data-bs-toggle="offcanvas" 
        data-bs-target="#settingsPanel">
        <i className="bi bi-sliders"></i> Settings
    </button>
    </header>
  )
};

export default Header;

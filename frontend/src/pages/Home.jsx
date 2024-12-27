// eslint-disable-next-line no-unused-vars
import React from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import MainPanel from '../components/MainPanel';

const Home = () => (
  <div className="container-fluid vh-100 d-flex flex-column">
    <Header />
    <div className="d-flex flex-grow-1">
      <Sidebar />
      <MainPanel />
    </div>
  </div>
);

export default Home;

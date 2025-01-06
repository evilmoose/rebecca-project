// eslint-disable-next-line no-unused-vars
import React from 'react';
import ChatContainer from './ChatContainer';
import PixijsContainer from './PixijsContainer';

const MainPanel = () => (
  <main className="main-panel d-flex flex-column">
    <div className="split-container">
      <ChatContainer />
      <PixijsContainer />
    </div>
  </main>
);

export default MainPanel;

// eslint-disable-next-line no-unused-vars
import React from 'react';
import ThreeJSContainer from './ThreeJSContainer';
import ChatContainer from './ChatContainer';

const MainPanel = () => (
  <main className="main-panel d-flex flex-column">
    <div className="split-container">
      <ChatContainer />
      <ThreeJSContainer />
    </div>
  </main>
);

export default MainPanel;

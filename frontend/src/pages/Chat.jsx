// eslint-disable-next-line no-unused-vars
import React from 'react';
import ChatContainer from '../components/ChatContainer';

const Chat = () => {
  

  return (
    <div className="container-fluid vh-100 d-flex flex-column">
      <header className="d-flex align-items-center px-3 py-2 border-bottom">
        <h2>Rebecca&apos;s Chat</h2>
      </header>
      <div className="flex-grow-1 d-flex flex-column border p-3">
      <main className="flex-grow-1 d-flex flex-column border p-3">
        <ChatContainer />
      </main>
      </div>
    </div>
  );
};

export default Chat;


// eslint-disable-next-line no-unused-vars
import React from 'react';

const Sidebar = () => (
  <nav className="sidebar border-end bg-white p-3">
    <ul className="list-unstyled">
      <li className="mb-3">
        <button className="btn btn-primary w-100">New Chat</button>
      </li>
      <li className="mb-3">
        <button className="btn btn-outline-secondary w-100">Archived Chats</button>
      </li>
      <li className="mb-3">
        <button className="btn btn-outline-secondary w-100">Workspace</button>
      </li>
    </ul>
  </nav>
);

export default Sidebar;

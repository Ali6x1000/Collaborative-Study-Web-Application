import React, { useState, useEffect } from 'react';
import './CollaboratorServer.css';

const CollaboratorServer = () => {
  const [serverStatus, setServerStatus] = useState(false);
  const [loading, setLoading] = useState(true);
  const collaboratorUrl = "http://localhost:5002";

  useEffect(() => {
    checkServerStatus();
    // Auto-refresh status every 30 seconds
    const interval = setInterval(checkServerStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkServerStatus = async () => {
    try {
      // Direct check to the collaborator server health endpoint
      const response = await fetch(`${collaboratorUrl}/health`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setServerStatus(data.status === 'healthy');
      } else {
        setServerStatus(false);
      }
    } catch (error) {
      // Server is not running or not accessible
      console.log('Collaborator server is not running:', error.message);
      setServerStatus(false);
    } finally {
      setLoading(false);
    }
  };

  const refreshStatus = () => {
    setLoading(true);
    checkServerStatus();
  };

  const openInNewTab = () => {
    window.open(collaboratorUrl, '_blank');
  };

  const showDockerInstructions = () => {
    alert('Please follow the Docker instructions shown on the page to start the collaborator server.');
  };

  const hideLoading = () => {
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="collaborator-server-page">
      <div className="header">
        <h1>Collaborator Server - PCA Handler</h1>
        <span className={`status-indicator ${serverStatus ? 'status-online' : 'status-offline'}`}>
          {serverStatus ? 'Online' : 'Offline'}
        </span>
      </div>
      
      <div className="server-controls">
        <button className="btn btn-primary" onClick={refreshStatus}>
          Refresh Status
        </button>
        <button className="btn btn-success" onClick={openInNewTab}>
          Open in New Tab
        </button>
        {!serverStatus && (
          <button className="btn btn-danger" onClick={showDockerInstructions}>
            Start Server
          </button>
        )}
      </div>
      
      {serverStatus ? (
        <div className="iframe-container">
          {loading && (
            <div className="loading-overlay">
              Loading Collaborator Server...
            </div>
          )}
          <iframe 
            src={collaboratorUrl} 
            onLoad={hideLoading}
            title="Collaborator Server"
          />
        </div>
      ) : (
        <div className="server-offline-message">
          <h2>Collaborator Server is Offline</h2>
          <p>The collaborator server needs to be running on your local machine to access the PCA Handler interface.</p>
          
          <div className="docker-instructions">
            <strong>To start the collaborator server:</strong><br/><br/>
            
            <strong>Option 1 - Run directly with Python:</strong><br/>
            <code>cd /Users/alinawaf/Desktop/Erman/Collaborative-Study-Web-Application/web_application/Backend/FlaskApp/Collaborator_Server</code><br/>
            <code>python gui_app.py</code><br/><br/>
            
            <strong>Option 2 - Using Docker:</strong><br/>
            1. Navigate to the collaborator server directory:<br/>
            <code>cd /Users/alinawaf/Desktop/Erman/Collaborative-Study-Web-Application/web_application/Backend/FlaskApp/Collaborator_Server</code><br/><br/>
            
            2. Build the Docker image:<br/>
            <code>docker build -t collaborator-server .</code><br/><br/>
            
            3. Run the container:<br/>
            <code>docker run -p 5002:5002 collaborator-server</code><br/><br/>
            
            4. The server will be available at: <a href={collaboratorUrl} target="_blank" rel="noopener noreferrer">{collaboratorUrl}</a>
          </div>
          
          <p style={{marginTop: '2rem'}}>
            <button className="btn btn-primary" onClick={refreshStatus}>
              Check Status Again
            </button>
          </p>
        </div>
      )}
    </div>
  );
};

export default CollaboratorServer;

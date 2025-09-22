// For Docker environment, use the external port mapping
const URL = process.env.NODE_ENV === 'production' 
  ? 'http://localhost:5011'  // Backend external port from docker-compose
  : 'http://localhost:5000'; // Development backend

export default URL;
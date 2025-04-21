const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// CORS configuration for Vercel
app.use(cors({
  origin: 'https://master.dq3hhwbwgg2a3.amplifyapp.com',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Log all requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', message: 'Proxy server is running' });
});

// Root endpoint
app.get('/', (req, res) => {
  res.status(200).json({
    status: 'online',
    message: 'Pine Time Proxy Server',
    endpoints: {
      '/health': 'Health check endpoint',
      '/api/...': 'API proxy endpoints'
    }
  });
});

// Proxy all API requests to your Elastic Beanstalk backend
app.use('/api', createProxyMiddleware({
  target: 'http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api/v1', // rewrite path
  },
  onProxyReq: (proxyReq, req, res) => {
    // Log proxy requests
    console.log(`Proxying ${req.method} ${req.url} → ${proxyReq.path}`);
  }
}));

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'Not found'
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({
    status: 'error',
    message: 'Internal server error'
  });
});

// Start the server if not being run by Vercel
if (process.env.NODE_ENV !== 'production') {
  app.listen(PORT, () => {
    console.log(`Proxy server running on port ${PORT}`);
  });
}

module.exports = app;


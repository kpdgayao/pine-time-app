const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// Configure CORS specifically for your Amplify domain
app.use(cors({
  origin: 'https://master.dq3hhwbwgg2a3.amplifyapp.com',
  credentials: true
}));

// Log all requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
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

app.listen(PORT, () => {
  console.log(`Proxy server running on port ${PORT}`);
});

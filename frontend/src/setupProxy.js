const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API requests to backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
    })
  );

  // Proxy WebSocket connections
  app.use(
    '/ws',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      ws: true,
    })
  );

  // Proxy health check
  app.use(
    '/health',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
    })
  );

  // Proxy docs
  app.use(
    '/docs',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
    })
  );
};
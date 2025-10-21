require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const supplierRoutes = require('./routes/supplierRoutes');

const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();
app.use(cors());
app.use(bodyParser.json());

/**
 * Swagger setup
 */
const swaggerOptions = {
  swaggerDefinition: {
    openapi: '3.0.0',
    info: {
      title: 'Supplier Service API',
      version: '1.0.0',
      description: 'API documentation for Supplier CRUD operations',
    },
    servers: [
      {
        url: 'https://info.ea2sa.com',
        description: 'Production server'
      },
    ],
  },
  apis: ['./routes/*.js'],
};
const swaggerDocs = swaggerJsdoc(swaggerOptions);

// ✅ Serve raw OpenAPI JSON spec
app.get('/swagger.json', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.send(swaggerDocs);
});

// ✅ Serve Swagger UI HTML (for browser)
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

/**
 * Supplier routes
 */
app.use('/api/suppliers', supplierRoutes);

const PORT = process.env.PORT || 3001;
const HOST = '0.0.0.0';

if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, HOST, () => {
    console.log(`Server running on http://${HOST}:${PORT}`);
    console.log(`Swagger UI at http://${HOST}:${PORT}/api-docs`);
    console.log(`Raw spec at http://${HOST}:${PORT}/swagger.json`);
  });
}

module.exports = app;

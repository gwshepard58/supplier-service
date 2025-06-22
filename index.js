require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const supplierRoutes = require('./routes/supplierRoutes');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use('/api/suppliers', supplierRoutes);

const PORT = process.env.PORT || 3001;
const HOST = '0.0.0.0';
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
  });
}

module.exports = app;

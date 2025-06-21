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
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`Supplier service running on port ${PORT}`);
  });
}

module.exports = app;

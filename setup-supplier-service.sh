#!/bin/bash
set -e

SERVICE_NAME="supplier-service"
DB_NAME="northwind"
DB_USER="gary"
DB_PASSWORD="Spen1cer"
PORT=3001

# Create service directory
mkdir -p "$SERVICE_NAME"
cd "$SERVICE_NAME"

# Initialize Node project
npm init -y

# Install dependencies
npm install express pg dotenv body-parser cors jest supertest

# Create folder structure
mkdir -p routes controllers config tests

# Create entry point
cat > index.js <<EOF
require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const supplierRoutes = require('./routes/supplierRoutes');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use('/api/suppliers', supplierRoutes);

const PORT = process.env.PORT || ${PORT};
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(\`Supplier service running on port \${PORT}\`);
  });
}

module.exports = app;
EOF

# Create supplier routes
cat > routes/supplierRoutes.js <<EOF
const express = require('express');
const router = express.Router();
const supplierController = require('../controllers/supplierController');

router.get('/', supplierController.getAllSuppliers);
router.get('/:id', supplierController.getSupplierById);
router.put('/:id', supplierController.updateSupplier);

module.exports = router;
EOF

# Create supplier controller
cat > controllers/supplierController.js <<EOF
const pool = require('../config/db');

exports.getAllSuppliers = async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM suppliers');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getSupplierById = async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM suppliers WHERE supplier_id = $1', [req.params.id]);
    if (result.rows.length === 0) return res.status(404).json({ error: "Supplier not found" });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.updateSupplier = async (req, res) => {
  const { company_name, contact_name, city } = req.body;
  try {
    const result = await pool.query(
      'UPDATE suppliers SET company_name = $1, contact_name = $2, city = $3 WHERE supplier_id = $4 RETURNING *',
      [company_name, contact_name, city, req.params.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: "Supplier not found" });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
EOF

# Create database config
cat > config/db.js <<EOF
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: 'localhost',
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: 5432,
});

module.exports = pool;
EOF

# Create .env file
cat > .env <<EOF
PORT=${PORT}
POSTGRES_DB=${DB_NAME}
POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=${DB_PASSWORD}
EOF

# Create Dockerfile
cat > Dockerfile <<EOF
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE ${PORT}
CMD ["node", "index.js"]
EOF

# Create test file
cat > tests/supplier.test.js <<EOF
const request = require('supertest');
const app = require('../index');

describe('GET /api/suppliers', () => {
  it('should return a list of suppliers', async () => {
    const res = await request(app).get('/api/suppliers');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBeTruthy();
  });
});
EOF

# Create Jest config in package.json
npx json -I -f package.json -e 'this.scripts.test="jest"'

echo "✅ Supplier microservice with testing initialized in ./$SERVICE_NAME"

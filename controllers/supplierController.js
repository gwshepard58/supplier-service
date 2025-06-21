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
    const result = await pool.query('SELECT * FROM suppliers WHERE supplier_id = ', [req.params.id]);
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
      'UPDATE suppliers SET company_name = , contact_name = , city =  WHERE supplier_id =  RETURNING *',
      [company_name, contact_name, city, req.params.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: "Supplier not found" });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

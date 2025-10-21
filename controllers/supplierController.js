const pool = require('../db'); 
const { getCache, setCache, deleteCache } = require('../utils/cache');

exports.getAllSuppliers = async (req, res) => {
  const cacheKey = 'suppliers:all';
  try {
    const cached = await getCache(cacheKey);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const result = await pool.query('SELECT * FROM suppliers');
    await setCache(cacheKey, JSON.stringify(result.rows));
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send('Error fetching suppliers');
  }
};

exports.getSupplierById = async (req, res) => {
  const id = req.params.id;
  const cacheKey = `suppliers:id:${id}`;
  try {
    const cached = await getCache(cacheKey);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const result = await pool.query('SELECT * FROM suppliers WHERE supplier_id = $1', [id]);
    if (result.rows.length === 0) {
      res.status(404).send('Supplier not found');
    } else {
      await setCache(cacheKey, JSON.stringify(result.rows[0]));
      res.json(result.rows[0]);
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('Error fetching supplier');
  }
};

exports.createSupplier = async (req, res) => {
  const { company_name, contact_name, contact_title, address, city, region, postal_code, country, phone } = req.body;
  try {
    const result = await pool.query(
      `INSERT INTO suppliers (company_name, contact_name, contact_title, address, city, region, postal_code, country, phone)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
       RETURNING *`,
      [company_name, contact_name, contact_title, address, city, region, postal_code, country, phone]
    );

    await deleteCache('suppliers:all'); // Invalidate cache
    await deleteCache('suppliers:count'); // also invalidate count cache
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).send('Error creating supplier');
  }
};

exports.updateSupplier = async (req, res) => {
  const id = req.params.id;
  const { company_name, contact_name, contact_title, address, city, region, postal_code, country, phone } = req.body;
  try {
    const result = await pool.query(
      `UPDATE suppliers
       SET company_name = $1, contact_name = $2, contact_title = $3, address = $4, city = $5,
           region = $6, postal_code = $7, country = $8, phone = $9
       WHERE supplier_id = $10
       RETURNING *`,
      [company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, id]
    );

    if (result.rows.length === 0) {
      res.status(404).send('Supplier not found');
    } else {
      await deleteCache('suppliers:all');
      await deleteCache('suppliers:count'); // invalidate count too
      await deleteCache(`suppliers:id:${id}`);
      res.json(result.rows[0]);
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('Error updating supplier');
  }
};

exports.deleteSupplier = async (req, res) => {
  const id = req.params.id;
  try {
    const result = await pool.query('DELETE FROM suppliers WHERE supplier_id = $1 RETURNING *', [id]);
    if (result.rows.length === 0) {
      res.status(404).send('Supplier not found');
    } else {
      await deleteCache('suppliers:all');
      await deleteCache('suppliers:count'); // invalidate count cache
      await deleteCache(`suppliers:id:${id}`);
      res.json({ message: 'Supplier deleted', supplier: result.rows[0] });
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('Error deleting supplier');
  }
};

// ✅ New: Get suppliers count
exports.getSuppliersCount = async (req, res) => {
  const cacheKey = 'suppliers:count';
  try {
    const cached = await getCache(cacheKey);
    if (cached) {
      return res.json({ count: Number(cached) });
    }

    const result = await pool.query('SELECT COUNT(*) FROM suppliers');
    const count = result.rows[0].count;

    await setCache(cacheKey, count);
    res.json({ count: Number(count) });
  } catch (err) {
    console.error(err);
    res.status(500).send('Error fetching supplier count');
  }
};

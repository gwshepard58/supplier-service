const express = require('express');
const router = express.Router();
const supplierController = require('../controllers/supplierController');

/**
 * @swagger
 * tags:
 *   name: Suppliers
 *   description: CRUD operations for suppliers
 */

/**
 * @swagger
 * /api/suppliers:
 *   get:
 *     summary: Retrieve all suppliers
 *     tags: [Suppliers]
 *     responses:
 *       200:
 *         description: List of suppliers
 */
router.get('/', supplierController.getAllSuppliers);

/**
 * @swagger
 * /api/suppliers/count:
 *   get:
 *     summary: Retrieve total supplier count
 *     tags: [Suppliers]
 *     responses:
 *       200:
 *         description: Supplier count
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 count:
 *                   type: integer
 *                   example: 1228
 */
router.get('/count', supplierController.getSuppliersCount);

/**
 * @swagger
 * /api/suppliers/{id}:
 *   get:
 *     summary: Retrieve a supplier by ID
 *     tags: [Suppliers]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         description: Supplier ID
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Supplier data
 *       404:
 *         description: Supplier not found
 */
router.get('/:id', supplierController.getSupplierById);

/**
 * @swagger
 * /api/suppliers:
 *   post:
 *     summary: Create a new supplier
 *     tags: [Suppliers]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *               contact:
 *                 type: string
 *     responses:
 *       201:
 *         description: Supplier created
 */
router.post('/', supplierController.createSupplier);

/**
 * @swagger
 * /api/suppliers/{id}:
 *   put:
 *     summary: Update an existing supplier
 *     tags: [Suppliers]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         description: Supplier ID
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *               contact:
 *                 type: string
 *     responses:
 *       200:
 *         description: Supplier updated
 *       404:
 *         description: Supplier not found
 */
router.put('/:id', supplierController.updateSupplier);

/**
 * @swagger
 * /api/suppliers/{id}:
 *   delete:
 *     summary: Delete a supplier
 *     tags: [Suppliers]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         description: Supplier ID
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Supplier deleted
 *       404:
 *         description: Supplier not found
 */
router.delete('/:id', supplierController.deleteSupplier);

module.exports = router;

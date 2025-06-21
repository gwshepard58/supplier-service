const request = require('supertest');
const app = require('../index');

describe('GET /api/suppliers', () => {
  it('should return a list of suppliers', async () => {
    const res = await request(app).get('/api/suppliers');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBeTruthy();
  });
});

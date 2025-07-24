const Memcached = require('memcached');

// Connect to local Memcached server or Docker container
const memcached = new Memcached('localhost:11211');

const CACHE_TTL = 60; // seconds

function getCache(key) {
  return new Promise((resolve, reject) => {
    memcached.get(key, (err, data) => {
      if (err) return reject(err);
      resolve(data);
    });
  });
}

function setCache(key, value, ttl = CACHE_TTL) {
  return new Promise((resolve, reject) => {
    memcached.set(key, value, ttl, (err) => {
      if (err) return reject(err);
      resolve(true);
    });
  });
}

function deleteCache(key) {
  return new Promise((resolve, reject) => {
    memcached.del(key, (err) => {
      if (err) return reject(err);
      resolve(true);
    });
  });
}

module.exports = {
  getCache,
  setCache,
  deleteCache,
};


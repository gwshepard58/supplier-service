const Memcached = require('memcached');

// Use direct IP of the container
const memcached = new Memcached('172.17.0.2:11211');

const CACHE_TTL = 60;

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

module.exports = { getCache, setCache, deleteCache };

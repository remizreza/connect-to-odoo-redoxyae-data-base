/**
 * Odoo JSON-RPC Client for redoxyae (Node.js)
 * Zero dependencies - uses native fetch / https.
 */

const fs = require('fs');
const path = require('path');

// Helper to load .env if present
function loadEnv() {
  const envPath = path.resolve(process.cwd(), '.env');
  if (fs.existsSync(envPath)) {
    const lines = fs.readFileSync(envPath, 'utf8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const idx = trimmed.indexOf('=');
      if (idx !== -1) {
        const key = trimmed.slice(0, idx).trim();
        const val = trimmed.slice(idx + 1).trim().replace(/^['"]|['"]$/g, '');
        if (!process.env[key]) {
          process.env[key] = val;
        }
      }
    }
  }
}

class OdooClient {
  constructor(options = {}) {
    loadEnv();
    this.url = (options.url || process.env.ODOO_URL || 'https://redoxyae.odoo.com').replace(/\/$/, '');
    this.db = options.db || process.env.ODOO_DB || 'redoxyae';
    this.username = options.username || process.env.ODOO_USER;
    this.password = options.password || process.env.ODOO_API_KEY || process.env.ODOO_PASSWORD;
    this.uid = null;
    this.requestId = 1;
  }

  async jsonRpc(service, method, args = []) {
    const payload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service,
        method,
        args,
      },
      id: this.requestId++,
    };

    const res = await fetch(`${this.url}/jsonrpc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP Error: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();
    if (data.error) {
      throw new Error(data.error.data?.message || data.error.message || JSON.stringify(data.error));
    }
    return data.result;
  }

  async getVersion() {
    return this.jsonRpc('common', 'version', []);
  }

  async authenticate(username, password) {
    const user = username || this.username;
    const key = password || this.password;
    if (!user || !key) {
      throw new Error('Username and API Key / Password are required.');
    }

    const uid = await this.jsonRpc('common', 'authenticate', [this.db, user, key, {}]);
    if (!uid) {
      throw new Error(`Authentication failed for user ${user} on database ${this.db}`);
    }
    this.uid = uid;
    this.username = user;
    this.password = key;
    return uid;
  }

  async executeKw(model, method, args = [], kwargs = {}) {
    if (!this.uid) {
      await this.authenticate();
    }
    return this.jsonRpc('object', 'execute_kw', [
      this.db,
      this.uid,
      this.password,
      model,
      method,
      args,
      kwargs,
    ]);
  }

  async searchRead(model, domain = [], fields = [], limit = 10, offset = 0, order = '') {
    const kwargs = { offset };
    if (fields && fields.length) kwargs.fields = fields;
    if (limit) kwargs.limit = limit;
    if (order) kwargs.order = order;
    return this.executeKw(model, 'search_read', [domain], kwargs);
  }

  async create(model, values) {
    return this.executeKw(model, 'create', [values]);
  }

  async write(model, ids, values) {
    const idList = Array.isArray(ids) ? ids : [ids];
    return this.executeKw(model, 'write', [idList, values]);
  }

  async unlink(model, ids) {
    const idList = Array.isArray(ids) ? ids : [ids];
    return this.executeKw(model, 'unlink', [idList]);
  }
}

if (require.main === module) {
  (async () => {
    try {
      const client = new OdooClient();
      console.log('Testing Odoo connection via JSON-RPC...');
      const version = await client.getVersion();
      console.log(`[OK] Server online! Version: ${version.server_version}`);
      console.log(`URL: ${client.url}`);
      console.log(`DB: ${client.db}`);
      if (client.username && client.password) {
        const uid = await client.authenticate();
        console.log(`[OK] Logged in successfully. UID: ${uid}`);
      } else {
        console.log('\nSet ODOO_USER and ODOO_API_KEY in .env to authenticate.');
      }
    } catch (err) {
      console.error('Error:', err.message);
    }
  })();
}

module.exports = { OdooClient };

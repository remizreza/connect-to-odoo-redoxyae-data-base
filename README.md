# Connect to Odoo Redoxyae Database

Tools and client libraries to connect, authenticate, and query the **Odoo SaaS database for Redoxyae** (`https://redoxyae.odoo.com`).

[![Odoo Server Status](https://img.shields.io/badge/Odoo_Server-Online_(saas~19.3+e)-10B981?style=flat-square)](https://redoxyae.odoo.com)
[![Protocol](https://img.shields.io/badge/Protocol-XML--RPC%20%7C%20JSON--RPC-blue?style=flat-square)](https://redoxyae.odoo.com)

---

## 🌐 Live Web Dashboard

You can access the interactive connection dashboard directly here:
👉 **[Open Redoxyae Connection Hub](https://antigravity.luch.dev/site/ef90ea0e-7f11-4311-b62a-aff645971b78/324e49e724f21e2de2e809d0/)**

The dashboard lets you:
- Inspect verified server and database connection parameters.
- Generate API keys and view step-by-step instructions.
- Create instant copy-paste snippets for Python, Node.js, CLI, and cURL.
- Browse common Odoo models (`res.partner`, `sale.order`, `product.template`, etc.).

---

## 📌 Database Parameters

- **Odoo Host:** `https://redoxyae.odoo.com`
- **Database Name:** `redoxyae`
- **Server Version:** `saas~19.3+e` (Odoo Online Enterprise)
- **Protocols Supported:** XML-RPC (`/xmlrpc/2/common`, `/xmlrpc/2/object`) and JSON-RPC (`/jsonrpc`)

---

## 🔑 Getting Your Odoo API Key

In modern Odoo (v14+ / v19 SaaS), using an **API Key** is recommended over using your account password:

1. Log into your Odoo account at [redoxyae.odoo.com](https://redoxyae.odoo.com).
2. Tap your user icon/name in the top-right corner and select **Preferences** (or **My Profile**).
3. Click the **Account Security** tab.
4. Under the **Developer API Keys** section, click **New API Key**.
5. Confirm your password, give the key a name (e.g. `Integration`), and copy the generated key.

---

## 🚀 Quick Start (Python)

### 1. Test Connection & Save Credentials

Run the diagnostic script with your credentials:

```bash
python3 test_connection.py --user your-email@example.com --key YOUR_API_KEY --save
```

This will:
- Check server reachability and version.
- Authenticate with the `redoxyae` database.
- Print your user and company details.
- Save your credentials into `.env` (which is safely git-ignored).

### 2. Query Data

Run the sample script:

```bash
python3 quickstart.py
```

### 3. Use in Your Code

```python
from odoo_client import OdooClient

client = OdooClient(
    url="https://redoxyae.odoo.com",
    db="redoxyae",
    username="your-email@example.com",
    password_or_key="YOUR_API_KEY",
)

# Authenticate
uid = client.authenticate()
print(f"Connected! UID: {uid}")

# Search and read customers
partners = client.search_read(
    model="res.partner",
    domain=[("customer_rank", ">", 0)],
    fields=["name", "email", "phone", "city"],
    limit=10,
    order="name asc",
)
for p in partners:
    print(p["name"], p.get("email"))
```

---

## 📦 JavaScript / Node.js Quick Start

```javascript
const { OdooClient } = require('./odoo_client');

async function main() {
  const client = new OdooClient({
    url: 'https://redoxyae.odoo.com',
    db: 'redoxyae',
    username: 'your-email@example.com',
    password: 'YOUR_API_KEY',
  });

  const uid = await client.authenticate();
  console.log(`Connected! UID: ${uid}`);

  const products = await client.searchRead('product.template', [], ['name', 'list_price'], 5);
  console.log(products);
}

main().catch(console.error);
```

---

## 📋 Common Odoo Models

| Model | Description | Common Fields |
|---|---|---|
| `res.partner` | Contacts, Customers, Vendors | `name`, `email`, `phone`, `city`, `is_company` |
| `sale.order` | Sales Quotes & Orders | `name`, `partner_id`, `amount_total`, `state` |
| `product.template` | Product Catalog | `name`, `list_price`, `type`, `qty_available` |
| `account.move` | Invoices & Bills | `name`, `partner_id`, `amount_total`, `state`, `invoice_date` |
| `crm.lead` | CRM Opportunities | `name`, `partner_id`, `expected_revenue`, `stage_id` |

---

## 🔒 Security Note

- Never commit credentials to git.
- `.env` and `*.log` files are already configured in `.gitignore`.
- Use Odoo Developer API keys instead of your primary password.

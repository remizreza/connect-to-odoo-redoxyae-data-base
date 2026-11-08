#!/usr/bin/env python3
"""
Quickstart example demonstrating how to interact with the redoxyae Odoo database.
Make sure you have configured .env or set environment variables:
    ODOO_USER=your-email@example.com
    ODOO_API_KEY=your-api-key
"""

from odoo_client import OdooClient


def main():
    client = OdooClient()
    print("Connecting to Odoo...")
    ver = client.get_version()
    print(f"Connected to Odoo server ({ver.get('server_version')}) at {client.url}")

    if not client.username or not client.password:
        print("\n[Notice] No credentials found in .env.")
        print("Please configure .env or pass credentials to OdooClient(username=..., password_or_key=...)")
        print("See .env.example for details.")
        return

    print(f"Authenticating as {client.username}...")
    uid = client.authenticate()
    print(f"Logged in as User ID: {uid}")

    # 1. Read Current User
    user = client.get_user_info()
    print(f"\n--- User Profile ---")
    print(f"Name   : {user.get('name')}")
    print(f"Email  : {user.get('email')}")
    print(f"Company: {user.get('company_id')}")

    # 2. Query Contacts / Customers (res.partner)
    print(f"\n--- Recent Contacts (res.partner) ---")
    contacts = client.search_read(
        "res.partner",
        domain=[],
        fields=["name", "email", "phone", "city", "country_id"],
        limit=5,
        order="id desc",
    )
    for c in contacts:
        print(f"[{c['id']}] {c.get('name')} | Email: {c.get('email') or 'N/A'} | Phone: {c.get('phone') or 'N/A'}")

    # 3. Query Products (product.template)
    print(f"\n--- Products (product.template) ---")
    try:
        products = client.search_read(
            "product.template",
            domain=[],
            fields=["name", "list_price", "type", "categ_id"],
            limit=5,
            order="id desc",
        )
        for p in products:
            print(f"[{p['id']}] {p.get('name')} | Price: ${p.get('list_price', 0):.2f}")
    except Exception as e:
        print(f"Could not load products: {e}")

    # 4. Example: How to create a new contact
    print(f"\n--- Code Example: Creating a new Contact ---")
    print("""
new_partner_id = client.create('res.partner', {
    'name': 'Acme Corporation',
    'is_company': True,
    'email': 'contact@acme.com',
    'phone': '+1 555-0199',
    'street': '123 Innovation Way',
    'city': 'Dubai',
})
print("Created Partner ID:", new_partner_id)
""")


if __name__ == "__main__":
    main()

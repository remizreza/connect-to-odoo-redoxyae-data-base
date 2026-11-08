#!/usr/bin/env python3
"""
Test connection script for Odoo redoxyae database.
Run:
    python3 test_connection.py
or:
    python3 test_connection.py --user your_email@domain.com --key your_api_key --save
"""

import argparse
import getpass
import os
import sys
from odoo_client import OdooClient, load_env


def test_connection(url: str, db: str, user: str, key: str, save_env: bool = False):
    print("=" * 60)
    print("  Odoo Connection Diagnostic & Tester")
    print("=" * 60)
    print(f"Target URL : {url}")
    print(f"Database   : {db}")
    print(f"User / API : {user or '(none specified)'}")
    print("-" * 60)

    # 1. Ping / Version check
    print("[1/4] Checking server reachability and version...")
    try:
        client = OdooClient(url=url, db=db, username=user, password_or_key=key)
        version_data = client.get_version()
        server_ver = version_data.get("server_version", "unknown")
        proto_ver = version_data.get("protocol_version", "unknown")
        print(f"  [OK] Server is reachable!")
        print(f"  [OK] Server Version: Odoo {server_ver}")
        print(f"  [OK] Protocol Version: {proto_ver}")
    except Exception as e:
        print(f"  [FAIL] Could not reach Odoo server: {e}", file=sys.stderr)
        return False

    # 2. Authentication check
    if not user or not key:
        print("\n[!] No user credentials supplied.")
        print("    Server connection is verified, but authentication cannot be tested.")
        print("\nTo test authentication, run:")
        print("    python3 test_connection.py --user your-email@domain.com --key YOUR_API_KEY")
        return True

    print("\n[2/4] Authenticating with database...")
    try:
        uid = client.authenticate(user, key)
        print(f"  [OK] Authenticated successfully!")
        print(f"  [OK] Assigned User ID (UID): {uid}")
    except PermissionError as e:
        print(f"  [FAIL] Authentication failed: {e}", file=sys.stderr)
        print("\nTip: Make sure you are using an API key generated from:")
        print("     Odoo Profile -> Preferences -> Account Security -> Developer API Keys -> New API Key")
        return False
    except Exception as e:
        print(f"  [FAIL] Connection error during auth: {e}", file=sys.stderr)
        return False

    # 3. Retrieve user & company profile
    print("\n[3/4] Fetching user profile & company details...")
    try:
        user_data = client.get_user_info()
        print(f"  [OK] User Name: {user_data.get('name')}")
        print(f"  [OK] User Login: {user_data.get('login')}")
        company = user_data.get("company_id")
        if company and isinstance(company, (list, tuple)) and len(company) > 1:
            print(f"  [OK] Company: {company[1]} (ID: {company[0]})")
    except Exception as e:
        print(f"  [WARN] Could not read user details: {e}")

    # 4. Probe common models
    print("\n[4/4] Probing database records...")
    models_to_probe = [
        ("res.partner", "Contacts / Partners"),
        ("res.users", "Active Users"),
        ("product.template", "Product Templates"),
        ("sale.order", "Sales Orders"),
        ("account.move", "Invoices / Accounting"),
        ("crm.lead", "CRM Leads"),
    ]

    for model_name, label in models_to_probe:
        try:
            count = client.search_count(model_name, [])
            print(f"  - {label} ({model_name}): {count} records found")
        except Exception:
            # Model might not be installed or restricted
            print(f"  - {label} ({model_name}): [not installed or restricted]")

    # Save to .env if requested
    if save_env:
        env_file = ".env"
        try:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"ODOO_URL={url}\n")
                f.write(f"ODOO_DB={db}\n")
                f.write(f"ODOO_USER={user}\n")
                f.write(f"ODOO_API_KEY={key}\n")
            print(f"\n[OK] Successfully saved configuration to {env_file} (git-ignored)")
        except Exception as e:
            print(f"\n[WARN] Failed to write {env_file}: {e}")

    print("\n" + "=" * 60)
    print("  Connection test completed successfully!")
    print("=" * 60)
    return True


def main():
    load_env()
    parser = argparse.ArgumentParser(description="Test Odoo redoxyae connection")
    parser.add_argument(
        "--url",
        default=os.environ.get("ODOO_URL", "https://redoxyae.odoo.com"),
        help="Odoo instance URL (default: https://redoxyae.odoo.com)",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("ODOO_DB", "redoxyae"),
        help="Odoo database name (default: redoxyae)",
    )
    parser.add_argument(
        "--user",
        default=os.environ.get("ODOO_USER"),
        help="Odoo user email / login",
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("ODOO_API_KEY") or os.environ.get("ODOO_PASSWORD"),
        help="Odoo API key or password",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save credentials to .env for future use",
    )
    args = parser.parse_args()

    user = args.user
    key = args.key

    # If running interactively in terminal without args or env vars, ask nicely
    if sys.stdin.isatty() and not user:
        try:
            prompt_user = input("Odoo User Email (leave blank to skip auth): ").strip()
            if prompt_user:
                user = prompt_user
                key = getpass.getpass("Odoo API Key or Password: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)

    test_connection(url=args.url, db=args.db, user=user, key=key, save_env=args.save)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Odoo API Client for redoxyae (Odoo SaaS 19+ / Enterprise / Community)
Zero external dependencies required - works with standard Python library.
"""

import os
import sys
import xmlrpc.client
from typing import Any, Dict, List, Optional, Union


def load_env(env_path: str = ".env") -> Dict[str, str]:
    """Parse a simple .env file into os.environ if it exists."""
    env_vars = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        env_vars[k] = v
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            print(f"[Notice] Could not load {env_path}: {e}", file=sys.stderr)
    return env_vars


class OdooClient:
    """
    Client for interacting with Odoo via XML-RPC.
    Preconfigured for redoxyae (https://redoxyae.odoo.com).
    """

    DEFAULT_URL = "https://redoxyae.odoo.com"
    DEFAULT_DB = "redoxyae"

    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        password_or_key: Optional[str] = None,
    ):
        load_env()
        self.url = (url or os.environ.get("ODOO_URL") or self.DEFAULT_URL).rstrip("/")
        self.db = db or os.environ.get("ODOO_DB") or self.DEFAULT_DB
        self.username = username or os.environ.get("ODOO_USER") or os.environ.get("ODOO_LOGIN")
        self.password = (
            password_or_key
            or os.environ.get("ODOO_API_KEY")
            or os.environ.get("ODOO_PASSWORD")
        )
        self.uid: Optional[int] = None
        self._common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self._models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def get_version(self) -> Dict[str, Any]:
        """Fetch Odoo server version details."""
        return self._common.version()

    def authenticate(
        self,
        username: Optional[str] = None,
        password_or_key: Optional[str] = None,
    ) -> int:
        """
        Authenticate against Odoo database.
        Returns user ID (uid). Raises ValueError if authentication fails.
        """
        user = username or self.username
        key = password_or_key or self.password

        if not user or not key:
            raise ValueError(
                "Missing credentials: username and password/API key are required to authenticate."
            )

        uid = self._common.authenticate(self.db, user, key, {})
        if not uid:
            raise PermissionError(
                f"Authentication failed for user '{user}' on database '{self.db}'. "
                "Please verify your email/login and Odoo API key or password."
            )

        self.username = user
        self.password = key
        self.uid = uid
        return uid

    def ensure_authenticated(self) -> int:
        """Ensure client has an authenticated user ID."""
        if self.uid is None:
            return self.authenticate()
        return self.uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute an Odoo ORM method via XML-RPC execute_kw.
        Example: execute_kw('res.partner', 'search', [[['is_company', '=', True]]])
        """
        uid = self.ensure_authenticated()
        args = args or []
        kwargs = kwargs or {}
        return self._models.execute_kw(
            self.db, uid, self.password, model, method, args, kwargs
        )

    def search(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> List[int]:
        """Search records matching a domain filter and return their record IDs."""
        domain = domain or []
        kwargs: Dict[str, Any] = {"offset": offset}
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        return self.execute_kw(model, "search", [domain], kwargs)

    def read(
        self,
        model: str,
        ids: Union[int, List[int]],
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Read specific fields from records by their IDs."""
        if isinstance(ids, int):
            ids = [ids]
        kwargs: Dict[str, Any] = {}
        if fields:
            kwargs["fields"] = fields
        return self.execute_kw(model, "read", [ids], kwargs)

    def search_read(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
        fields: Optional[List[str]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search and read records in a single RPC call."""
        domain = domain or []
        kwargs: Dict[str, Any] = {"offset": offset}
        if fields:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [domain], kwargs)

    def search_count(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
    ) -> int:
        """Return the count of records matching the domain filter."""
        domain = domain or []
        return self.execute_kw(model, "search_count", [domain])

    def create(self, model: str, values: Dict[str, Any]) -> int:
        """Create a new record and return its new ID."""
        return self.execute_kw(model, "create", [values])

    def write(
        self,
        model: str,
        ids: Union[int, List[int]],
        values: Dict[str, Any],
    ) -> bool:
        """Update existing records."""
        if isinstance(ids, int):
            ids = [ids]
        return self.execute_kw(model, "write", [ids, values])

    def unlink(self, model: str, ids: Union[int, List[int]]) -> bool:
        """Delete records by ID."""
        if isinstance(ids, int):
            ids = [ids]
        return self.execute_kw(model, "unlink", [ids])

    def fields_get(
        self,
        model: str,
        fields: Optional[List[str]] = None,
        attributes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Fetch model field definitions and metadata."""
        kwargs: Dict[str, Any] = {}
        if attributes:
            kwargs["attributes"] = attributes
        return self.execute_kw(model, "fields_get", [fields or []], kwargs)

    def get_user_info(self) -> Dict[str, Any]:
        """Return current authenticated user profile information."""
        uid = self.ensure_authenticated()
        records = self.read(
            "res.users",
            [uid],
            ["name", "login", "email", "company_id", "active", "tz", "lang"],
        )
        return records[0] if records else {"id": uid}


if __name__ == "__main__":
    client = OdooClient()
    print("Connecting to Odoo server...")
    try:
        ver = client.get_version()
        print(f"Server is online! Version: {ver.get('server_version')} (Protocol: {ver.get('protocol_version')})")
        print(f"Target URL: {client.url}")
        print(f"Database: {client.db}")
        if client.username and client.password:
            print(f"Attempting authentication as {client.username}...")
            uid = client.authenticate()
            print(f"Authenticated successfully! User ID (uid): {uid}")
            user_info = client.get_user_info()
            print(f"User details: {user_info}")
        else:
            print("\nTo authenticate, set ODOO_USER and ODOO_API_KEY in .env or run:")
            print("  python3 test_connection.py --user <your-email> --key <your-api-key>")
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)

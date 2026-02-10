"""
Odoo JSON-RPC Client

Gold Tier Implementation: Uses Odoo's JSON-RPC API (Odoo 17+/19+ compatible)
instead of XML-RPC, as required by the hackathon specification.

Reference: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from config import config, LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger('OdooClient')


@dataclass
class OdooResult:
    """Result wrapper for Odoo operations."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class OdooJSONRPCClient:
    """
    JSON-RPC client for Odoo Community.

    Uses Odoo's /jsonrpc endpoint for all operations:
    - Authentication via 'call' service
    - CRUD via 'object' service execute_kw
    - Version info via 'common' service

    This replaces the previous XML-RPC implementation to comply
    with the Gold Tier requirement for JSON-RPC (Odoo 19+ architecture).
    """

    _request_id = 0

    def __init__(self, url: str = None, db: str = None,
                 username: str = None, password: str = None):
        """Initialize Odoo JSON-RPC client."""
        self.url = (url or config.url).rstrip('/')
        self.db = db or config.database
        self.username = username or config.username
        self.password = password or config.password
        self.uid: Optional[int] = None
        self.timeout = config.timeout

        logger.info(f"OdooJSONRPCClient initialized for {self.url}")

    def _next_id(self) -> int:
        """Get next JSON-RPC request ID."""
        OdooJSONRPCClient._request_id += 1
        return OdooJSONRPCClient._request_id

    def _jsonrpc_call(self, service: str, method: str, args: list) -> Any:
        """
        Make a raw JSON-RPC call to Odoo.

        Args:
            service: Odoo service ('common', 'object', 'db')
            method: Method name on the service
            args: Positional arguments for the method

        Returns:
            The 'result' field from the JSON-RPC response

        Raises:
            Exception on network or Odoo-level errors
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args
            },
            "id": self._next_id()
        }

        data = json.dumps(payload).encode('utf-8')
        endpoint = f"{self.url}/jsonrpc"

        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach Odoo at {endpoint}: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Odoo: {e}")

        if body.get("error"):
            err = body["error"]
            err_msg = err.get("data", {}).get("message") or err.get("message", str(err))
            raise RuntimeError(f"Odoo JSON-RPC error: {err_msg}")

        return body.get("result")

    # ========== Authentication ==========

    def connect(self) -> OdooResult:
        """
        Authenticate with Odoo via JSON-RPC.

        Returns:
            OdooResult with uid on success
        """
        try:
            uid = self._jsonrpc_call(
                "common", "authenticate",
                [self.db, self.username, self.password, {}]
            )

            if uid:
                self.uid = uid
                logger.info(f"Authenticated as uid={self.uid}")
                return OdooResult(success=True, data={"uid": self.uid})
            else:
                return OdooResult(
                    success=False,
                    error="Authentication failed - invalid credentials",
                    error_code="AUTH_FAILED"
                )
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return OdooResult(success=False, error=str(e), error_code="CONNECTION_ERROR")
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return OdooResult(success=False, error=str(e), error_code="AUTH_ERROR")

    def _ensure_connected(self) -> bool:
        """Ensure client is authenticated."""
        if not self.uid:
            result = self.connect()
            return result.success
        return True

    # ========== Core CRUD via execute_kw ==========

    def execute(self, model: str, method: str, *args, **kwargs) -> OdooResult:
        """
        Execute a method on an Odoo model via JSON-RPC.

        Args:
            model: Odoo model name (e.g., 'res.partner')
            method: ORM method (e.g., 'search', 'create', 'write')
            *args: Positional arguments for the method
            **kwargs: Keyword arguments passed as the options dict

        Returns:
            OdooResult with method result
        """
        if not self._ensure_connected():
            return OdooResult(
                success=False,
                error="Not connected to Odoo",
                error_code="NOT_CONNECTED"
            )

        try:
            result = self._jsonrpc_call(
                "object", "execute_kw",
                [self.db, self.uid, self.password,
                 model, method,
                 list(args),
                 kwargs if kwargs else {}]
            )
            return OdooResult(success=True, data=result)

        except RuntimeError as e:
            logger.error(f"Execute error on {model}.{method}: {e}")
            return OdooResult(success=False, error=str(e), error_code="EXECUTE_ERROR")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return OdooResult(success=False, error=str(e), error_code="UNEXPECTED_ERROR")

    # ========== Convenience Methods ==========

    def search(self, model: str, domain: List, limit: int = None,
               offset: int = 0, order: str = None) -> OdooResult:
        """Search for record IDs matching domain."""
        kwargs = {'offset': offset}
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        return self.execute(model, 'search', domain, **kwargs)

    def read(self, model: str, ids: List[int], fields: List[str] = None) -> OdooResult:
        """Read specific records by ID."""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        return self.execute(model, 'read', ids, **kwargs)

    def search_read(self, model: str, domain: List = None,
                    fields: List[str] = None, limit: int = None,
                    offset: int = 0, order: str = None) -> OdooResult:
        """Search and read records in one call."""
        kwargs = {'offset': offset}
        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        return self.execute(model, 'search_read', domain or [], **kwargs)

    def create(self, model: str, values: Dict) -> OdooResult:
        """Create a new record."""
        return self.execute(model, 'create', values)

    def write(self, model: str, ids: List[int], values: Dict) -> OdooResult:
        """Update existing records."""
        return self.execute(model, 'write', ids, values)

    def unlink(self, model: str, ids: List[int]) -> OdooResult:
        """Delete records."""
        return self.execute(model, 'unlink', ids)

    def get_version(self) -> OdooResult:
        """Get Odoo server version via JSON-RPC."""
        try:
            version = self._jsonrpc_call("common", "version", [])
            return OdooResult(success=True, data=version)
        except Exception as e:
            return OdooResult(success=False, error=str(e))

    def test_connection(self) -> OdooResult:
        """Test full connection: version + authenticate."""
        version_result = self.get_version()
        if not version_result.success:
            return version_result

        auth_result = self.connect()
        if not auth_result.success:
            return auth_result

        return OdooResult(
            success=True,
            data={
                'server_version': version_result.data.get('server_version', 'unknown'),
                'protocol': 'JSON-RPC',
                'uid': self.uid,
                'database': self.db
            }
        )


# Singleton instance
_client: Optional[OdooJSONRPCClient] = None


def get_client() -> OdooJSONRPCClient:
    """Get or create the Odoo JSON-RPC client."""
    global _client
    if _client is None:
        _client = OdooJSONRPCClient()
    return _client

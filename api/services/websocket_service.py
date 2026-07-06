"""WebSocket service for real-time scan updates."""
import json
import asyncio
from typing import Set, Dict, Any
from datetime import datetime
from fastapi import WebSocket
from api.db.models import CIScanHistory


class ConnectionManager:
    """Manage WebSocket connections and broadcasts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[str, Set[WebSocket]] = {}  # repo_name -> connections
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, repository: str = "all"):
        """Register a new WebSocket connection."""
        await websocket.accept()
        async with self.lock:
            self.active_connections.add(websocket)
            if repository not in self.subscriptions:
                self.subscriptions[repository] = set()
            self.subscriptions[repository].add(websocket)
        print(f"Client connected (repository: {repository}). Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket, repository: str = "all"):
        """Unregister a WebSocket connection."""
        async with self.lock:
            self.active_connections.discard(websocket)
            if repository in self.subscriptions:
                self.subscriptions[repository].discard(websocket)
                if not self.subscriptions[repository]:
                    del self.subscriptions[repository]
        print(f"Client disconnected (repository: {repository}). Total: {len(self.active_connections)}")

    async def broadcast_scan_complete(self, scan: CIScanHistory):
        """Broadcast scan completion to all connected clients."""
        message = {
            "type": "scan_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "id": scan.id,
                "repository": scan.repository,
                "branch": scan.branch,
                "platform": scan.platform,
                "status": scan.status,
                "critical_count": scan.critical_count,
                "error_count": scan.error_count,
                "warning_count": scan.warning_count,
                "total_findings": scan.total_findings,
                "files_scanned": scan.files_scanned,
                "duration_ms": scan.duration_ms,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
            }
        }
        await self._broadcast(message, scan.repository)

    async def broadcast_dashboard_refresh(self, summary: Dict[str, Any]):
        """Broadcast dashboard summary refresh."""
        message = {
            "type": "dashboard_refresh",
            "timestamp": datetime.utcnow().isoformat(),
            "data": summary
        }
        await self._broadcast(message, "all")

    async def broadcast_alert(self, repository: str, alert_type: str, content: Dict[str, Any]):
        """Broadcast alert to relevant clients."""
        message = {
            "type": "alert",
            "alert_type": alert_type,
            "timestamp": datetime.utcnow().isoformat(),
            "repository": repository,
            "data": content
        }
        await self._broadcast(message, repository)

    async def broadcast_scan_progress(self, scan_id: str, progress: int, repository: str):
        """Broadcast scan progress (0-100)."""
        message = {
            "type": "scan_progress",
            "timestamp": datetime.utcnow().isoformat(),
            "scan_id": scan_id,
            "progress": progress,
            "repository": repository,
        }
        await self._broadcast(message, repository)

    async def _broadcast(self, message: Dict[str, Any], repository: str):
        """Internal method to broadcast to subscribed clients."""
        async with self.lock:
            # Get all clients to notify
            targets = set()

            # Always include "all" subscribers
            if "all" in self.subscriptions:
                targets.update(self.subscriptions["all"])

            # Include repository-specific subscribers
            if repository != "all" and repository in self.subscriptions:
                targets.update(self.subscriptions[repository])

            # Send to all targets
            disconnected = []
            message_json = json.dumps(message)

            for websocket in targets:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    print(f"Failed to send message: {e}")
                    disconnected.append(websocket)

            # Clean up disconnected clients
            for ws in disconnected:
                self.active_connections.discard(ws)

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to a specific client."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Failed to send personal message: {e}")

    async def send_heartbeat(self, websocket: WebSocket):
        """Send periodic heartbeat to keep connection alive."""
        try:
            message = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
            }
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Failed to send heartbeat: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                repo: len(clients)
                for repo, clients in self.subscriptions.items()
            }
        }


# Global connection manager
manager = ConnectionManager()

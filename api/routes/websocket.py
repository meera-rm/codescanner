"""WebSocket routes for real-time updates."""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from api.services.websocket_service import manager

router = APIRouter(prefix="/api/v1/ws", tags=["websocket"])


@router.websocket("/scans")
async def websocket_scans(
    websocket: WebSocket,
    repository: str = Query("all", description="Repository to subscribe to ('all' for all repos)"),
):
    """
    WebSocket endpoint for real-time scan updates.

    **Connection:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/scans?repository=all');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('Update:', message);
    };
    ```

    **Message Types:**
    - `scan_complete`: New scan completed
    - `dashboard_refresh`: Dashboard summary updated
    - `scan_progress`: Scan in progress (0-100%)
    - `alert`: Alert triggered
    - `heartbeat`: Keep-alive signal

    **Example Messages:**

    Scan Complete:
    ```json
    {
      "type": "scan_complete",
      "timestamp": "2026-07-06T12:34:56.789Z",
      "data": {
        "id": "scan-uuid",
        "repository": "my-repo",
        "branch": "main",
        "platform": "github",
        "status": "success",
        "critical_count": 0,
        "error_count": 2,
        "warning_count": 15,
        "total_findings": 22,
        "files_scanned": 150,
        "duration_ms": 5000,
        "created_at": "2026-07-06T12:34:56.789Z"
      }
    }
    ```

    Dashboard Refresh:
    ```json
    {
      "type": "dashboard_refresh",
      "timestamp": "2026-07-06T12:34:56.789Z",
      "data": {
        "total_scans": 487,
        "successful_scans": 450,
        "failed_scans": 37,
        "pass_rate": 92.4,
        "total_critical": 5,
        "total_error": 23,
        "total_warning": 156
      }
    }
    ```

    Scan Progress:
    ```json
    {
      "type": "scan_progress",
      "timestamp": "2026-07-06T12:34:56.789Z",
      "scan_id": "scan-uuid",
      "progress": 75,
      "repository": "my-repo"
    }
    ```

    Alert:
    ```json
    {
      "type": "alert",
      "alert_type": "critical_threshold_exceeded",
      "timestamp": "2026-07-06T12:34:56.789Z",
      "repository": "my-repo",
      "data": {
        "critical_count": 1,
        "threshold": 1,
        "message": "Critical issues found!"
      }
    }
    ```

    Heartbeat:
    ```json
    {
      "type": "heartbeat",
      "timestamp": "2026-07-06T12:34:56.789Z"
    }
    ```

    **Query Parameters:**
    - `repository`: Repository name to subscribe to. Use "all" to receive updates for all repos.

    **Status Codes:**
    - 101: WebSocket connection established
    - 1000: Normal closure
    - 1001: Going away
    - 1002: Protocol error
    - 1003: Unsupported data
    """
    await manager.connect(websocket, repository)

    try:
        # Send welcome message
        await manager.send_personal_message(
            websocket,
            {
                "type": "connected",
                "message": f"Connected to repository: {repository}",
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

        # Periodically send heartbeat
        heartbeat_task = asyncio.create_task(_heartbeat_loop(websocket))

        while True:
            # Keep connection open and receive messages
            data = await websocket.receive_text()
            # Echo client messages back with server timestamp
            await manager.send_personal_message(
                websocket,
                {
                    "type": "echo",
                    "message": data,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, repository)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket, repository)


@router.websocket("/dashboard")
async def websocket_dashboard(
    websocket: WebSocket,
):
    """
    WebSocket endpoint for dashboard real-time updates.

    Receives dashboard summary updates, scan completions, and alerts.
    Auto-refreshes the dashboard without page reload.

    **Connection:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/dashboard');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'dashboard_refresh') {
        updateDashboard(message.data);
      }
    };
    ```
    """
    await manager.connect(websocket, "all")

    try:
        # Send welcome message
        await manager.send_personal_message(
            websocket,
            {
                "type": "connected",
                "message": "Connected to dashboard updates",
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

        # Periodically send heartbeat
        heartbeat_task = asyncio.create_task(_heartbeat_loop(websocket))

        while True:
            # Keep connection open
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        await manager.disconnect(websocket, "all")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket, "all")


@router.get("/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics.

    **Response:**
    ```json
    {
      "total_connections": 5,
      "subscriptions": {
        "all": 3,
        "my-repo": 2,
        "other-repo": 1
      }
    }
    ```
    """
    return manager.get_stats()


async def _heartbeat_loop(websocket: WebSocket, interval: int = 30):
    """Send periodic heartbeat to keep WebSocket alive."""
    try:
        while True:
            await asyncio.sleep(interval)
            await manager.send_heartbeat(websocket)
    except Exception as e:
        print(f"Heartbeat failed: {e}")

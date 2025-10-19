"""
Master server for Shards of Eternity multiplayer.

REST API and WebSocket server for player authentication, character management,
world state synchronization, and real-time updates.
"""
import asyncio
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from contextlib import asynccontextmanager

import aiohttp
from aiohttp import web
import aiohttp_cors
from sqlalchemy.orm import Session

from config.settings import get_settings
from database import get_db_session
from database.models import (
    Character, Party, CrystalShard, WorldState, WorldEvent,
    FactionType, RealityType, ShardOwnership
)
from network.protocol import (
    protocol, ProtocolError, MessageType,
    AuthRequest, AuthResponse, ChatMessage, WorldStateMessage,
    create_auth_response, create_world_state_message, create_shard_captured_message
)

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================================
# Session Management
# ============================================================================

class PlayerSession:
    """Represents an active player session."""

    def __init__(self, session_token: str, player_id: int, username: str,
                 character_id: Optional[int] = None):
        self.session_token = session_token
        self.player_id = player_id
        self.username = username
        self.character_id = character_id
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.websocket: Optional[web.WebSocketResponse] = None

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def is_expired(self, timeout_seconds: int = 3600) -> bool:
        """Check if session has expired."""
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return elapsed > timeout_seconds


class SessionManager:
    """Manages active player sessions."""

    def __init__(self):
        self.sessions: Dict[str, PlayerSession] = {}
        self.player_sessions: Dict[int, str] = {}  # player_id -> session_token
        self.websockets: Set[web.WebSocketResponse] = set()

    def create_session(self, player_id: int, username: str,
                      character_id: Optional[int] = None) -> PlayerSession:
        """Create a new player session."""
        # Invalidate any existing session for this player
        if player_id in self.player_sessions:
            old_token = self.player_sessions[player_id]
            self.sessions.pop(old_token, None)

        # Generate secure session token
        session_token = secrets.token_urlsafe(32)

        session = PlayerSession(session_token, player_id, username, character_id)
        self.sessions[session_token] = session
        self.player_sessions[player_id] = session_token

        logger.info(f"Created session for player {username} (ID: {player_id})")
        return session

    def get_session(self, session_token: str) -> Optional[PlayerSession]:
        """Get session by token."""
        session = self.sessions.get(session_token)
        if session and not session.is_expired():
            session.update_activity()
            return session
        elif session:
            # Session expired
            self.invalidate_session(session_token)
        return None

    def invalidate_session(self, session_token: str):
        """Invalidate a session."""
        session = self.sessions.pop(session_token, None)
        if session:
            self.player_sessions.pop(session.player_id, None)
            if session.websocket:
                self.websockets.discard(session.websocket)
            logger.info(f"Invalidated session for player {session.username}")

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        expired = [
            token for token, session in self.sessions.items()
            if session.is_expired()
        ]
        for token in expired:
            self.invalidate_session(token)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

    def get_active_player_count(self) -> int:
        """Get count of active players."""
        self.cleanup_expired_sessions()
        return len(self.sessions)

    def get_session_by_player_id(self, player_id: int) -> Optional[PlayerSession]:
        """Get session by player ID."""
        token = self.player_sessions.get(player_id)
        if token:
            return self.get_session(token)
        return None


# ============================================================================
# Master Server
# ============================================================================

class MasterServer:
    """
    Master server handling authentication, world state, and coordination.
    """

    def __init__(self, host: str = None, port: int = None):
        self.host = host or settings.master_server_host
        self.port = port or settings.master_server_port
        self.app = web.Application()
        self.session_manager = SessionManager()
        self.runner: Optional[web.AppRunner] = None

        # Setup routes
        self._setup_routes()

        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None

    def _setup_routes(self):
        """Setup HTTP routes and WebSocket endpoints."""
        # REST API endpoints
        self.app.router.add_post("/api/auth/login", self.handle_login)
        self.app.router.add_post("/api/auth/register", self.handle_register)
        self.app.router.add_post("/api/auth/logout", self.handle_logout)

        self.app.router.add_get("/api/characters", self.handle_get_characters)
        self.app.router.add_post("/api/characters", self.handle_create_character)
        self.app.router.add_post("/api/characters/select", self.handle_select_character)
        self.app.router.add_delete("/api/characters/{character_id}", self.handle_delete_character)

        self.app.router.add_get("/api/world/state", self.handle_get_world_state)
        self.app.router.add_get("/api/world/shards", self.handle_get_shards)
        self.app.router.add_get("/api/world/events", self.handle_get_events)

        self.app.router.add_get("/api/party/{party_id}", self.handle_get_party)
        self.app.router.add_post("/api/party/create", self.handle_create_party)
        self.app.router.add_post("/api/party/invite", self.handle_party_invite)
        self.app.router.add_post("/api/party/leave", self.handle_party_leave)

        self.app.router.add_get("/api/status", self.handle_status)

        # WebSocket endpoint
        self.app.router.add_get("/ws", self.handle_websocket)

        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Apply CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    # ========================================================================
    # Authentication Endpoints
    # ========================================================================

    async def handle_login(self, request: web.Request) -> web.Response:
        """Handle player login."""
        try:
            data = await request.json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return web.json_response(
                    {"success": False, "message": "Username and password required"},
                    status=400
                )

            # TODO: Implement actual password verification
            # For now, we'll use a simple player lookup
            with get_db_session() as session:
                # In a real implementation, you'd have a Player/User table
                # For now, we'll just create a simple session
                player_id = hash(username) % 1000000  # Simple player ID generation

                # Create session
                player_session = self.session_manager.create_session(
                    player_id=player_id,
                    username=username
                )

                return web.json_response({
                    "success": True,
                    "session_token": player_session.session_token,
                    "player_id": player_id,
                    "username": username,
                    "message": "Login successful"
                })

        except Exception as e:
            logger.error(f"Login error: {e}")
            return web.json_response(
                {"success": False, "message": f"Login failed: {str(e)}"},
                status=500
            )

    async def handle_register(self, request: web.Request) -> web.Response:
        """Handle player registration."""
        try:
            data = await request.json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return web.json_response(
                    {"success": False, "message": "Username and password required"},
                    status=400
                )

            # TODO: Implement actual user registration with password hashing
            # For now, return success
            return web.json_response({
                "success": True,
                "message": "Registration successful. Please login."
            })

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return web.json_response(
                {"success": False, "message": f"Registration failed: {str(e)}"},
                status=500
            )

    async def handle_logout(self, request: web.Request) -> web.Response:
        """Handle player logout."""
        try:
            data = await request.json()
            session_token = data.get("session_token")

            if session_token:
                self.session_manager.invalidate_session(session_token)

            return web.json_response({"success": True, "message": "Logged out"})

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return web.json_response(
                {"success": False, "message": f"Logout failed: {str(e)}"},
                status=500
            )

    # ========================================================================
    # Character Management Endpoints
    # ========================================================================

    async def handle_get_characters(self, request: web.Request) -> web.Response:
        """Get list of characters for authenticated player."""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = self.session_manager.get_session(session_token)

        if not session:
            return web.json_response(
                {"error": "Unauthorized"},
                status=401
            )

        try:
            with get_db_session() as db_session:
                # In a real implementation, filter by player_id
                # For now, return all player characters
                characters = db_session.query(Character).filter(
                    Character.is_player == True
                ).all()

                return web.json_response({
                    "characters": [char.to_dict() for char in characters]
                })

        except Exception as e:
            logger.error(f"Get characters error: {e}")
            return web.json_response(
                {"error": f"Failed to get characters: {str(e)}"},
                status=500
            )

    async def handle_create_character(self, request: web.Request) -> web.Response:
        """Create a new character."""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = self.session_manager.get_session(session_token)

        if not session:
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            data = await request.json()

            # TODO: Use CharacterCreator from characters.character module
            # For now, return success message
            return web.json_response({
                "success": True,
                "message": "Character creation endpoint - implement with CharacterCreator"
            })

        except Exception as e:
            logger.error(f"Create character error: {e}")
            return web.json_response(
                {"error": f"Failed to create character: {str(e)}"},
                status=500
            )

    async def handle_select_character(self, request: web.Request) -> web.Response:
        """Select a character for the current session."""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = self.session_manager.get_session(session_token)

        if not session:
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            data = await request.json()
            character_id = data.get("character_id")

            if not character_id:
                return web.json_response(
                    {"error": "character_id required"},
                    status=400
                )

            with get_db_session() as db_session:
                character = db_session.query(Character).filter(
                    Character.id == character_id
                ).first()

                if not character:
                    return web.json_response(
                        {"error": "Character not found"},
                        status=404
                    )

                # Update session
                session.character_id = character_id

                return web.json_response({
                    "success": True,
                    "character": character.to_dict()
                })

        except Exception as e:
            logger.error(f"Select character error: {e}")
            return web.json_response(
                {"error": f"Failed to select character: {str(e)}"},
                status=500
            )

    async def handle_delete_character(self, request: web.Request) -> web.Response:
        """Delete a character."""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = self.session_manager.get_session(session_token)

        if not session:
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            character_id = int(request.match_info["character_id"])

            with get_db_session() as db_session:
                character = db_session.query(Character).filter(
                    Character.id == character_id
                ).first()

                if not character:
                    return web.json_response(
                        {"error": "Character not found"},
                        status=404
                    )

                db_session.delete(character)
                db_session.commit()

                return web.json_response({
                    "success": True,
                    "message": f"Character {character.name} deleted"
                })

        except Exception as e:
            logger.error(f"Delete character error: {e}")
            return web.json_response(
                {"error": f"Failed to delete character: {str(e)}"},
                status=500
            )

    # ========================================================================
    # World State Endpoints
    # ========================================================================

    async def handle_get_world_state(self, request: web.Request) -> web.Response:
        """Get current world state."""
        try:
            with get_db_session() as db_session:
                world_state = db_session.query(WorldState).first()

                if not world_state:
                    # Create default world state
                    world_state = WorldState(
                        current_reality=RealityType.NEUTRAL,
                        reality_stability=100.0,
                        aetherfall_count=0,
                        total_aetherfalls=0,
                        active_players=self.session_manager.get_active_player_count()
                    )
                    db_session.add(world_state)
                    db_session.commit()

                # Get shard distribution
                shards = db_session.query(CrystalShard).all()
                faction_counts = {}
                for shard in shards:
                    if shard.owning_faction:
                        faction = shard.owning_faction.value
                        faction_counts[faction] = faction_counts.get(faction, 0) + 1

                return web.json_response({
                    "current_reality": world_state.current_reality.value,
                    "reality_stability": world_state.reality_stability,
                    "faction_shard_counts": faction_counts,
                    "dominant_faction": world_state.dominant_faction.value if world_state.dominant_faction else None,
                    "active_players": self.session_manager.get_active_player_count(),
                    "total_aetherfalls": world_state.total_aetherfalls,
                    "aetherfall_count": world_state.aetherfall_count
                })

        except Exception as e:
            logger.error(f"Get world state error: {e}")
            return web.json_response(
                {"error": f"Failed to get world state: {str(e)}"},
                status=500
            )

    async def handle_get_shards(self, request: web.Request) -> web.Response:
        """Get information about all Crystal Shards."""
        try:
            with get_db_session() as db_session:
                shards = db_session.query(CrystalShard).all()

                shard_data = []
                for shard in shards:
                    shard_data.append({
                        "id": shard.id,
                        "shard_number": shard.shard_number,
                        "name": shard.shard_name,
                        "description": shard.description,
                        "location_id": shard.location_id,
                        "is_captured": shard.is_captured,
                        "owning_faction": shard.owning_faction.value if shard.owning_faction else None,
                        "guardian_name": shard.guardian_boss_name,
                        "guardian_defeated": shard.guardian_defeated,
                        "power_level": shard.power_level
                    })

                return web.json_response({"shards": shard_data})

        except Exception as e:
            logger.error(f"Get shards error: {e}")
            return web.json_response(
                {"error": f"Failed to get shards: {str(e)}"},
                status=500
            )

    async def handle_get_events(self, request: web.Request) -> web.Response:
        """Get recent world events."""
        try:
            limit = int(request.query.get("limit", "50"))

            with get_db_session() as db_session:
                events = db_session.query(WorldEvent).order_by(
                    WorldEvent.timestamp.desc()
                ).limit(limit).all()

                event_data = []
                for event in events:
                    event_data.append({
                        "id": event.id,
                        "event_type": event.event_type,
                        "title": event.title,
                        "description": event.description,
                        "timestamp": event.timestamp.isoformat(),
                        "faction": event.faction.value if event.faction else None
                    })

                return web.json_response({"events": event_data})

        except Exception as e:
            logger.error(f"Get events error: {e}")
            return web.json_response(
                {"error": f"Failed to get events: {str(e)}"},
                status=500
            )

    # ========================================================================
    # Party Management Endpoints
    # ========================================================================

    async def handle_get_party(self, request: web.Request) -> web.Response:
        """Get party information."""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = self.session_manager.get_session(session_token)

        if not session:
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            party_id = int(request.match_info["party_id"])

            with get_db_session() as db_session:
                party = db_session.query(Party).filter(Party.id == party_id).first()

                if not party:
                    return web.json_response({"error": "Party not found"}, status=404)

                return web.json_response({
                    "id": party.id,
                    "party_name": party.party_name,
                    "leader_id": party.leader_id,
                    "is_active": party.is_active,
                    "max_members": party.max_members,
                    "member_count": len(party.members),
                    "loot_sharing": party.loot_sharing
                })

        except Exception as e:
            logger.error(f"Get party error: {e}")
            return web.json_response(
                {"error": f"Failed to get party: {str(e)}"},
                status=500
            )

    async def handle_create_party(self, request: web.Request) -> web.Response:
        """Create a new party."""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = self.session_manager.get_session(session_token)

        if not session or not session.character_id:
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            data = await request.json()
            party_name = data.get("party_name", "Adventuring Party")

            with get_db_session() as db_session:
                party = Party(
                    party_name=party_name,
                    leader_id=session.character_id,
                    is_active=True
                )
                db_session.add(party)
                db_session.commit()
                db_session.refresh(party)

                return web.json_response({
                    "success": True,
                    "party_id": party.id,
                    "party_name": party.party_name
                })

        except Exception as e:
            logger.error(f"Create party error: {e}")
            return web.json_response(
                {"error": f"Failed to create party: {str(e)}"},
                status=500
            )

    async def handle_party_invite(self, request: web.Request) -> web.Response:
        """Invite a player to party."""
        # TODO: Implement party invitation logic
        return web.json_response({
            "success": False,
            "message": "Party invite endpoint - to be implemented"
        })

    async def handle_party_leave(self, request: web.Request) -> web.Response:
        """Leave current party."""
        # TODO: Implement party leave logic
        return web.json_response({
            "success": False,
            "message": "Party leave endpoint - to be implemented"
        })

    # ========================================================================
    # Status & Health Check
    # ========================================================================

    async def handle_status(self, request: web.Request) -> web.Response:
        """Server status endpoint."""
        return web.json_response({
            "status": "online",
            "version": "1.0.0",
            "active_players": self.session_manager.get_active_player_count(),
            "active_sessions": len(self.session_manager.sessions),
            "websocket_connections": len(self.session_manager.websockets),
            "uptime": "N/A"  # TODO: Track server start time
        })

    # ========================================================================
    # WebSocket Handler
    # ========================================================================

    async def handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        session_token = None
        player_session = None

        logger.info("New WebSocket connection established")
        self.session_manager.websockets.add(ws)

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        # Deserialize message
                        message = protocol.deserialize(msg.data)

                        # Handle authentication
                        if message.type == MessageType.AUTH_REQUEST:
                            auth_msg: AuthRequest = message
                            # Verify session token or credentials
                            if auth_msg.session_token:
                                player_session = self.session_manager.get_session(
                                    auth_msg.session_token
                                )
                                if player_session:
                                    player_session.websocket = ws
                                    session_token = auth_msg.session_token
                                    response = create_auth_response(
                                        success=True,
                                        session_token=session_token,
                                        player_id=player_session.player_id,
                                        message="WebSocket authenticated"
                                    )
                                else:
                                    response = create_auth_response(
                                        success=False,
                                        message="Invalid session token"
                                    )
                            else:
                                response = create_auth_response(
                                    success=False,
                                    message="Session token required"
                                )

                            await ws.send_str(protocol.serialize(response))

                        # Handle chat messages
                        elif message.type in [MessageType.CHAT, MessageType.PARTY_CHAT,
                                             MessageType.FACTION_CHAT]:
                            if player_session:
                                # Broadcast to appropriate channels
                                await self._broadcast_message(message, player_session)

                        # Handle ping/pong
                        elif message.type == MessageType.PING:
                            pong = protocol.serialize(BaseMessage(type=MessageType.PONG))
                            await ws.send_str(pong)

                    except ProtocolError as e:
                        logger.error(f"Protocol error: {e}")
                        error = protocol.create_error_message(
                            "PROTOCOL_ERROR",
                            str(e)
                        )
                        await ws.send_str(protocol.serialize(error))

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")

        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")

        finally:
            self.session_manager.websockets.discard(ws)
            if player_session and player_session.websocket == ws:
                player_session.websocket = None
            logger.info("WebSocket connection closed")

        return ws

    async def _broadcast_message(self, message: ChatMessage, sender_session: PlayerSession):
        """Broadcast a message to appropriate recipients."""
        serialized = protocol.serialize(message)

        # Determine recipients based on channel
        recipients = []
        if message.channel == "global":
            # Broadcast to all connected websockets
            recipients = list(self.session_manager.websockets)
        elif message.channel == "party":
            # TODO: Get party members' websockets
            pass
        elif message.channel == "faction":
            # TODO: Get faction members' websockets
            pass

        # Send to all recipients
        for ws in recipients:
            try:
                if not ws.closed:
                    await ws.send_str(serialized)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

    # ========================================================================
    # Server Lifecycle
    # ========================================================================

    async def start(self):
        """Start the master server."""
        logger.info(f"Starting master server on {self.host}:{self.port}")

        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        # Start web server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()

        logger.info(f"Master server running on http://{self.host}:{self.port}")

    async def stop(self):
        """Stop the master server."""
        logger.info("Stopping master server...")

        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()

        # Close all websockets
        for ws in list(self.session_manager.websockets):
            await ws.close()

        # Stop web server
        if self.runner:
            await self.runner.cleanup()

        logger.info("Master server stopped")

    async def _cleanup_loop(self):
        """Background task to cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                self.session_manager.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run the master server."""
    server = MasterServer()

    try:
        await server.start()
        # Keep running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())

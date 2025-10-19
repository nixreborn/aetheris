"""
Shards of Eternity - Networking Module

Provides multiplayer networking capabilities including:
- Protocol definitions and message serialization
- Master server for authentication and world state
- P2P client for real-time communication
"""

from network.protocol import (
    protocol,
    ProtocolHandler,
    ProtocolError,
    MessageType,
    MessagePriority,
    BaseMessage,
    AuthRequest,
    AuthResponse,
    ChatMessage,
    CharacterUpdateMessage,
    MoveMessage,
    PartyInviteMessage,
    PartyUpdateMessage,
    CombatActionMessage,
    CombatStateMessage,
    ShardCapturedMessage,
    WorldStateMessage,
    ErrorMessage,
    create_auth_request,
    create_auth_response,
    create_chat_message,
    create_character_update,
    create_move_message,
    create_party_invite,
    create_shard_captured_message,
    create_world_state_message,
)

from network.master_server import (
    MasterServer,
    PlayerSession,
    SessionManager,
)

from network.peer import (
    NetworkClient,
    NearbyPlayer,
    EncryptionHandler,
    create_client_and_connect,
)

__all__ = [
    # Protocol
    "protocol",
    "ProtocolHandler",
    "ProtocolError",
    "MessageType",
    "MessagePriority",
    "BaseMessage",
    "AuthRequest",
    "AuthResponse",
    "ChatMessage",
    "CharacterUpdateMessage",
    "MoveMessage",
    "PartyInviteMessage",
    "PartyUpdateMessage",
    "CombatActionMessage",
    "CombatStateMessage",
    "ShardCapturedMessage",
    "WorldStateMessage",
    "ErrorMessage",
    "create_auth_request",
    "create_auth_response",
    "create_chat_message",
    "create_character_update",
    "create_move_message",
    "create_party_invite",
    "create_shard_captured_message",
    "create_world_state_message",
    # Master Server
    "MasterServer",
    "PlayerSession",
    "SessionManager",
    # P2P Client
    "NetworkClient",
    "NearbyPlayer",
    "EncryptionHandler",
    "create_client_and_connect",
]

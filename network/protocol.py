"""
Network protocol definitions for Shards of Eternity multiplayer.

Defines message types, serialization/deserialization, validation,
and protocol version handling for client-server and P2P communication.
"""
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass, asdict, field
from pydantic import BaseModel, Field, validator, ValidationError

logger = logging.getLogger(__name__)

# Protocol version - increment when making breaking changes
PROTOCOL_VERSION = "1.0.0"


class MessageType(str, Enum):
    """
    All possible message types in the Shards of Eternity protocol.
    """
    # Authentication & Connection
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"

    # Character Management
    CHARACTER_LIST = "character_list"
    CHARACTER_SELECT = "character_select"
    CHARACTER_CREATE = "character_create"
    CHARACTER_UPDATE = "character_update"
    CHARACTER_DELETE = "character_delete"

    # Movement & Location
    MOVE = "move"
    LOCATION_UPDATE = "location_update"
    PLAYER_JOINED_AREA = "player_joined_area"
    PLAYER_LEFT_AREA = "player_left_area"

    # Chat & Communication
    CHAT = "chat"
    WHISPER = "whisper"
    PARTY_CHAT = "party_chat"
    FACTION_CHAT = "faction_chat"
    WORLD_ANNOUNCEMENT = "world_announcement"

    # Party System
    PARTY_CREATE = "party_create"
    PARTY_INVITE = "party_invite"
    PARTY_ACCEPT = "party_accept"
    PARTY_DECLINE = "party_decline"
    PARTY_LEAVE = "party_leave"
    PARTY_KICK = "party_kick"
    PARTY_DISBAND = "party_disband"
    PARTY_UPDATE = "party_update"

    # Combat
    COMBAT_START = "combat_start"
    COMBAT_ACTION = "combat_action"
    COMBAT_DAMAGE = "combat_damage"
    COMBAT_HEAL = "combat_heal"
    COMBAT_END = "combat_end"
    COMBAT_STATE = "combat_state"

    # World State
    WORLD_STATE = "world_state"
    SHARD_CAPTURED = "shard_captured"
    SHARD_STATUS = "shard_status"
    REALITY_SHIFT = "reality_shift"
    AETHERFALL = "aetherfall"

    # Trading & Economy
    TRADE_REQUEST = "trade_request"
    TRADE_ACCEPT = "trade_accept"
    TRADE_DECLINE = "trade_decline"
    TRADE_UPDATE = "trade_update"
    TRADE_COMPLETE = "trade_complete"

    # Quests & Events
    QUEST_UPDATE = "quest_update"
    EVENT_TRIGGER = "event_trigger"

    # Errors
    ERROR = "error"
    INVALID_MESSAGE = "invalid_message"


class MessagePriority(int, Enum):
    """Message priority for queue ordering."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# ============================================================================
# Pydantic Models for Message Validation
# ============================================================================

class BaseMessage(BaseModel):
    """Base message structure with common fields."""
    type: MessageType
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    version: str = PROTOCOL_VERSION
    message_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL

    class Config:
        use_enum_values = True


class AuthRequest(BaseMessage):
    """Authentication request from client."""
    type: MessageType = MessageType.AUTH_REQUEST
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    session_token: Optional[str] = None


class AuthResponse(BaseMessage):
    """Authentication response from server."""
    type: MessageType = MessageType.AUTH_RESPONSE
    success: bool
    session_token: Optional[str] = None
    player_id: Optional[int] = None
    message: Optional[str] = None
    server_time: float = Field(default_factory=lambda: datetime.utcnow().timestamp())


class ChatMessage(BaseMessage):
    """Chat message."""
    type: MessageType = MessageType.CHAT
    sender_id: int
    sender_name: str
    channel: str = "global"  # global, party, faction, whisper
    content: str = Field(..., min_length=1, max_length=500)
    recipient_id: Optional[int] = None  # For whispers


class CharacterUpdateMessage(BaseMessage):
    """Character state update."""
    type: MessageType = MessageType.CHARACTER_UPDATE
    character_id: int
    character_name: str
    location_id: Optional[int] = None
    position: Optional[Dict[str, float]] = None
    health: Optional[int] = None
    max_health: Optional[int] = None
    mana: Optional[int] = None
    max_mana: Optional[int] = None
    stamina: Optional[int] = None
    max_stamina: Optional[int] = None
    level: Optional[int] = None
    faction: Optional[str] = None


class MoveMessage(BaseMessage):
    """Movement update."""
    type: MessageType = MessageType.MOVE
    character_id: int
    from_location_id: Optional[int] = None
    to_location_id: int
    position: Optional[Dict[str, float]] = None  # x, y, z coordinates
    velocity: Optional[Dict[str, float]] = None


class PartyInviteMessage(BaseMessage):
    """Party invitation."""
    type: MessageType = MessageType.PARTY_INVITE
    party_id: int
    inviter_id: int
    inviter_name: str
    invitee_id: int
    invitee_name: str
    party_name: Optional[str] = None


class PartyUpdateMessage(BaseMessage):
    """Party state update."""
    type: MessageType = MessageType.PARTY_UPDATE
    party_id: int
    party_name: Optional[str] = None
    leader_id: int
    member_ids: List[int]
    member_names: List[str]
    max_members: int = 4
    loot_sharing: str = "equal"


class CombatActionMessage(BaseMessage):
    """Combat action from player."""
    type: MessageType = MessageType.COMBAT_ACTION
    combat_id: str
    character_id: int
    action_type: str  # attack, defend, spell, item, flee
    target_id: Optional[int] = None
    ability_name: Optional[str] = None
    item_id: Optional[int] = None


class CombatStateMessage(BaseMessage):
    """Combat state synchronization."""
    type: MessageType = MessageType.COMBAT_STATE
    combat_id: str
    turn_number: int
    active_character_id: int
    participants: List[Dict[str, Any]]
    combat_log: List[str]
    is_finished: bool = False


class ShardCapturedMessage(BaseMessage):
    """Shard capture event."""
    type: MessageType = MessageType.SHARD_CAPTURED
    priority: MessagePriority = MessagePriority.HIGH
    shard_id: int
    shard_name: str
    captured_by_character_id: int
    captured_by_character_name: str
    faction: str
    previous_owner_faction: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())


class WorldStateMessage(BaseMessage):
    """World state snapshot."""
    type: MessageType = MessageType.WORLD_STATE
    current_reality: str
    reality_stability: float
    faction_shard_counts: Dict[str, int]
    dominant_faction: Optional[str] = None
    active_players: int
    total_aetherfalls: int


class ErrorMessage(BaseMessage):
    """Error message."""
    type: MessageType = MessageType.ERROR
    priority: MessagePriority = MessagePriority.HIGH
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# Message Registry - Maps message types to their Pydantic models
# ============================================================================

MESSAGE_MODELS = {
    MessageType.AUTH_REQUEST: AuthRequest,
    MessageType.AUTH_RESPONSE: AuthResponse,
    MessageType.CHAT: ChatMessage,
    MessageType.PARTY_CHAT: ChatMessage,
    MessageType.FACTION_CHAT: ChatMessage,
    MessageType.WHISPER: ChatMessage,
    MessageType.CHARACTER_UPDATE: CharacterUpdateMessage,
    MessageType.MOVE: MoveMessage,
    MessageType.PARTY_INVITE: PartyInviteMessage,
    MessageType.PARTY_UPDATE: PartyUpdateMessage,
    MessageType.COMBAT_ACTION: CombatActionMessage,
    MessageType.COMBAT_STATE: CombatStateMessage,
    MessageType.SHARD_CAPTURED: ShardCapturedMessage,
    MessageType.WORLD_STATE: WorldStateMessage,
    MessageType.ERROR: ErrorMessage,
}


# ============================================================================
# Protocol Handler
# ============================================================================

class ProtocolError(Exception):
    """Raised when protocol validation fails."""
    pass


class ProtocolHandler:
    """
    Handles message serialization, deserialization, and validation.
    """

    def __init__(self, supported_versions: Optional[List[str]] = None):
        """
        Initialize protocol handler.

        Args:
            supported_versions: List of supported protocol versions
        """
        self.supported_versions = supported_versions or [PROTOCOL_VERSION]
        self.logger = logging.getLogger(__name__)

    def serialize(self, message: BaseMessage) -> str:
        """
        Serialize a message object to JSON string.

        Args:
            message: Message object (must inherit from BaseMessage)

        Returns:
            JSON string representation

        Raises:
            ProtocolError: If serialization fails
        """
        try:
            # Convert Pydantic model to dict, then to JSON
            message_dict = message.dict()
            json_str = json.dumps(message_dict, default=str)
            return json_str
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")
            raise ProtocolError(f"Failed to serialize message: {e}")

    def deserialize(self, json_str: str) -> BaseMessage:
        """
        Deserialize JSON string to message object.

        Args:
            json_str: JSON string

        Returns:
            Validated message object

        Raises:
            ProtocolError: If deserialization or validation fails
        """
        try:
            # Parse JSON
            data = json.loads(json_str)

            # Validate protocol version
            version = data.get("version", "unknown")
            if version not in self.supported_versions:
                raise ProtocolError(
                    f"Unsupported protocol version: {version}. "
                    f"Supported: {self.supported_versions}"
                )

            # Get message type
            msg_type_str = data.get("type")
            if not msg_type_str:
                raise ProtocolError("Message missing 'type' field")

            try:
                msg_type = MessageType(msg_type_str)
            except ValueError:
                raise ProtocolError(f"Unknown message type: {msg_type_str}")

            # Get appropriate model for this message type
            model_class = MESSAGE_MODELS.get(msg_type, BaseMessage)

            # Validate and create message object
            message = model_class(**data)

            return message

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            raise ProtocolError(f"Invalid JSON: {e}")
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            raise ProtocolError(f"Message validation failed: {e}")
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            raise ProtocolError(f"Failed to deserialize message: {e}")

    def validate_message(self, message: Union[BaseMessage, Dict]) -> bool:
        """
        Validate a message structure.

        Args:
            message: Message object or dictionary

        Returns:
            True if valid

        Raises:
            ProtocolError: If validation fails
        """
        try:
            if isinstance(message, dict):
                # Try to deserialize
                msg_type = MessageType(message.get("type"))
                model_class = MESSAGE_MODELS.get(msg_type, BaseMessage)
                model_class(**message)
            elif isinstance(message, BaseMessage):
                # Already validated by Pydantic
                pass
            else:
                raise ProtocolError(f"Invalid message type: {type(message)}")

            return True
        except Exception as e:
            raise ProtocolError(f"Validation failed: {e}")

    def create_error_message(
        self,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> ErrorMessage:
        """
        Create a standardized error message.

        Args:
            error_code: Error code (e.g., "AUTH_FAILED", "INVALID_MESSAGE")
            error_message: Human-readable error message
            details: Additional error details

        Returns:
            ErrorMessage object
        """
        return ErrorMessage(
            error_code=error_code,
            error_message=error_message,
            details=details
        )

    def is_version_compatible(self, version: str) -> bool:
        """
        Check if a protocol version is compatible.

        Args:
            version: Protocol version string

        Returns:
            True if compatible
        """
        return version in self.supported_versions


# ============================================================================
# Message Builders - Convenience functions for creating common messages
# ============================================================================

def create_auth_request(username: str, password: str, session_token: Optional[str] = None) -> AuthRequest:
    """Create authentication request."""
    return AuthRequest(username=username, password=password, session_token=session_token)


def create_auth_response(success: bool, session_token: Optional[str] = None,
                         player_id: Optional[int] = None, message: Optional[str] = None) -> AuthResponse:
    """Create authentication response."""
    return AuthResponse(
        success=success,
        session_token=session_token,
        player_id=player_id,
        message=message
    )


def create_chat_message(sender_id: int, sender_name: str, content: str,
                       channel: str = "global", recipient_id: Optional[int] = None) -> ChatMessage:
    """Create chat message."""
    msg_type = MessageType.CHAT
    if channel == "whisper":
        msg_type = MessageType.WHISPER
    elif channel == "party":
        msg_type = MessageType.PARTY_CHAT
    elif channel == "faction":
        msg_type = MessageType.FACTION_CHAT

    return ChatMessage(
        type=msg_type,
        sender_id=sender_id,
        sender_name=sender_name,
        content=content,
        channel=channel,
        recipient_id=recipient_id
    )


def create_character_update(character_id: int, character_name: str, **kwargs) -> CharacterUpdateMessage:
    """Create character update message."""
    return CharacterUpdateMessage(
        character_id=character_id,
        character_name=character_name,
        **kwargs
    )


def create_move_message(character_id: int, to_location_id: int,
                       from_location_id: Optional[int] = None,
                       position: Optional[Dict[str, float]] = None) -> MoveMessage:
    """Create movement message."""
    return MoveMessage(
        character_id=character_id,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        position=position
    )


def create_party_invite(party_id: int, inviter_id: int, inviter_name: str,
                       invitee_id: int, invitee_name: str,
                       party_name: Optional[str] = None) -> PartyInviteMessage:
    """Create party invitation."""
    return PartyInviteMessage(
        party_id=party_id,
        inviter_id=inviter_id,
        inviter_name=inviter_name,
        invitee_id=invitee_id,
        invitee_name=invitee_name,
        party_name=party_name
    )


def create_shard_captured_message(shard_id: int, shard_name: str,
                                  character_id: int, character_name: str,
                                  faction: str, previous_faction: Optional[str] = None) -> ShardCapturedMessage:
    """Create shard capture notification."""
    return ShardCapturedMessage(
        shard_id=shard_id,
        shard_name=shard_name,
        captured_by_character_id=character_id,
        captured_by_character_name=character_name,
        faction=faction,
        previous_owner_faction=previous_faction
    )


def create_world_state_message(current_reality: str, reality_stability: float,
                               faction_shard_counts: Dict[str, int],
                               dominant_faction: Optional[str] = None,
                               active_players: int = 0,
                               total_aetherfalls: int = 0) -> WorldStateMessage:
    """Create world state snapshot."""
    return WorldStateMessage(
        current_reality=current_reality,
        reality_stability=reality_stability,
        faction_shard_counts=faction_shard_counts,
        dominant_faction=dominant_faction,
        active_players=active_players,
        total_aetherfalls=total_aetherfalls
    )


# ============================================================================
# Module-level protocol handler instance
# ============================================================================

protocol = ProtocolHandler()

"""
Unit tests for the Shards of Eternity networking system.

Tests protocol serialization, message validation, and basic client-server communication.
"""
import pytest
import asyncio
import json
from datetime import datetime

from network.protocol import (
    protocol,
    ProtocolHandler,
    ProtocolError,
    MessageType,
    MessagePriority,
    create_auth_request,
    create_auth_response,
    create_chat_message,
    create_character_update,
    create_move_message,
    create_shard_captured_message,
    create_world_state_message,
)

from network.master_server import SessionManager, PlayerSession
from network.peer import EncryptionHandler


# ============================================================================
# Protocol Tests
# ============================================================================

class TestProtocol:
    """Test protocol serialization and validation."""

    def test_protocol_handler_creation(self):
        """Test creating a protocol handler."""
        handler = ProtocolHandler()
        assert handler is not None
        assert len(handler.supported_versions) > 0

    def test_serialize_auth_request(self):
        """Test serializing an auth request."""
        msg = create_auth_request("testuser", "testpass")
        serialized = protocol.serialize(msg)

        assert isinstance(serialized, str)
        data = json.loads(serialized)
        assert data["type"] == "auth_request"
        assert data["username"] == "testuser"
        assert data["password"] == "testpass"

    def test_deserialize_auth_request(self):
        """Test deserializing an auth request."""
        msg = create_auth_request("testuser", "testpass")
        serialized = protocol.serialize(msg)
        deserialized = protocol.deserialize(serialized)

        assert deserialized.type == MessageType.AUTH_REQUEST
        assert deserialized.username == "testuser"
        assert deserialized.password == "testpass"

    def test_serialize_chat_message(self):
        """Test serializing a chat message."""
        msg = create_chat_message(
            sender_id=1,
            sender_name="TestPlayer",
            content="Hello, world!",
            channel="global"
        )
        serialized = protocol.serialize(msg)

        assert isinstance(serialized, str)
        data = json.loads(serialized)
        assert data["type"] == "chat"
        assert data["sender_name"] == "TestPlayer"
        assert data["content"] == "Hello, world!"

    def test_deserialize_chat_message(self):
        """Test deserializing a chat message."""
        msg = create_chat_message(
            sender_id=1,
            sender_name="TestPlayer",
            content="Hello, world!"
        )
        serialized = protocol.serialize(msg)
        deserialized = protocol.deserialize(serialized)

        assert deserialized.type == MessageType.CHAT
        assert deserialized.sender_name == "TestPlayer"
        assert deserialized.content == "Hello, world!"

    def test_serialize_character_update(self):
        """Test serializing a character update."""
        msg = create_character_update(
            character_id=1,
            character_name="Hero",
            location_id=5,
            health=80,
            max_health=100,
            level=10
        )
        serialized = protocol.serialize(msg)

        data = json.loads(serialized)
        assert data["character_id"] == 1
        assert data["character_name"] == "Hero"
        assert data["health"] == 80
        assert data["level"] == 10

    def test_serialize_move_message(self):
        """Test serializing a move message."""
        msg = create_move_message(
            character_id=1,
            to_location_id=5,
            from_location_id=4,
            position={"x": 100.0, "y": 50.0, "z": 0.0}
        )
        serialized = protocol.serialize(msg)

        data = json.loads(serialized)
        assert data["character_id"] == 1
        assert data["to_location_id"] == 5
        assert data["from_location_id"] == 4
        assert data["position"]["x"] == 100.0

    def test_serialize_shard_captured(self):
        """Test serializing a shard capture message."""
        msg = create_shard_captured_message(
            shard_id=1,
            shard_name="Phoenix Flame",
            character_id=5,
            character_name="Hero",
            faction="Crimson Covenant"
        )
        serialized = protocol.serialize(msg)

        data = json.loads(serialized)
        assert data["shard_id"] == 1
        assert data["shard_name"] == "Phoenix Flame"
        assert data["faction"] == "Crimson Covenant"

    def test_serialize_world_state(self):
        """Test serializing a world state message."""
        msg = create_world_state_message(
            current_reality="Neutral",
            reality_stability=95.5,
            faction_shard_counts={"Crimson Covenant": 3, "Aether Seekers": 2},
            active_players=10
        )
        serialized = protocol.serialize(msg)

        data = json.loads(serialized)
        assert data["current_reality"] == "Neutral"
        assert data["reality_stability"] == 95.5
        assert data["active_players"] == 10

    def test_invalid_json(self):
        """Test that invalid JSON raises ProtocolError."""
        with pytest.raises(ProtocolError):
            protocol.deserialize("{invalid json")

    def test_missing_type_field(self):
        """Test that missing type field raises ProtocolError."""
        with pytest.raises(ProtocolError):
            protocol.deserialize('{"username": "test"}')

    def test_unknown_message_type(self):
        """Test that unknown message type raises ProtocolError."""
        with pytest.raises(ProtocolError):
            protocol.deserialize('{"type": "unknown_type", "version": "1.0.0"}')

    def test_message_priority(self):
        """Test message priority assignment."""
        msg = create_chat_message(1, "Test", "Hello")
        assert msg.priority == MessagePriority.NORMAL

        shard_msg = create_shard_captured_message(
            1, "Shard", 1, "Hero", "Faction"
        )
        assert shard_msg.priority == MessagePriority.HIGH

    def test_timestamp_generation(self):
        """Test that timestamps are automatically generated."""
        msg = create_chat_message(1, "Test", "Hello")
        assert msg.timestamp is not None
        assert isinstance(msg.timestamp, float)


# ============================================================================
# Session Manager Tests
# ============================================================================

class TestSessionManager:
    """Test session management."""

    def test_create_session(self):
        """Test creating a player session."""
        manager = SessionManager()
        session = manager.create_session(
            player_id=1,
            username="testuser"
        )

        assert session is not None
        assert session.player_id == 1
        assert session.username == "testuser"
        assert session.session_token is not None

    def test_get_session(self):
        """Test retrieving a session."""
        manager = SessionManager()
        session = manager.create_session(1, "testuser")

        retrieved = manager.get_session(session.session_token)
        assert retrieved is not None
        assert retrieved.player_id == 1
        assert retrieved.username == "testuser"

    def test_get_nonexistent_session(self):
        """Test retrieving a nonexistent session."""
        manager = SessionManager()
        session = manager.get_session("invalid_token")
        assert session is None

    def test_invalidate_session(self):
        """Test invalidating a session."""
        manager = SessionManager()
        session = manager.create_session(1, "testuser")
        token = session.session_token

        manager.invalidate_session(token)

        retrieved = manager.get_session(token)
        assert retrieved is None

    def test_session_expiration(self):
        """Test that expired sessions are not returned."""
        manager = SessionManager()
        session = manager.create_session(1, "testuser")

        # Manually expire the session
        session.last_activity = datetime(2000, 1, 1)

        retrieved = manager.get_session(session.session_token)
        assert retrieved is None

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        manager = SessionManager()

        # Create sessions
        s1 = manager.create_session(1, "user1")
        s2 = manager.create_session(2, "user2")

        # Expire one
        s1.last_activity = datetime(2000, 1, 1)

        # Cleanup
        manager.cleanup_expired_sessions()

        # Check that expired session is removed
        assert manager.get_session(s1.session_token) is None
        assert manager.get_session(s2.session_token) is not None

    def test_active_player_count(self):
        """Test getting active player count."""
        manager = SessionManager()

        assert manager.get_active_player_count() == 0

        manager.create_session(1, "user1")
        manager.create_session(2, "user2")

        assert manager.get_active_player_count() == 2

    def test_session_token_uniqueness(self):
        """Test that session tokens are unique."""
        manager = SessionManager()

        s1 = manager.create_session(1, "user1")
        s2 = manager.create_session(2, "user2")

        assert s1.session_token != s2.session_token

    def test_replace_existing_session(self):
        """Test that creating a new session invalidates old one."""
        manager = SessionManager()

        s1 = manager.create_session(1, "user1")
        old_token = s1.session_token

        s2 = manager.create_session(1, "user1")  # Same player_id
        new_token = s2.session_token

        assert old_token != new_token
        assert manager.get_session(old_token) is None
        assert manager.get_session(new_token) is not None


# ============================================================================
# Encryption Tests
# ============================================================================

class TestEncryption:
    """Test message encryption/decryption."""

    def test_encryption_handler_creation(self):
        """Test creating an encryption handler."""
        handler = EncryptionHandler()
        assert handler is not None
        assert handler.key is not None

    def test_encrypt_decrypt(self):
        """Test encrypting and decrypting a message."""
        handler = EncryptionHandler()

        original = "Hello, world!"
        encrypted = handler.encrypt(original)
        decrypted = handler.decrypt(encrypted)

        assert encrypted != original
        assert decrypted == original

    def test_encrypt_decrypt_json(self):
        """Test encrypting and decrypting JSON messages."""
        handler = EncryptionHandler()

        msg = create_chat_message(1, "Test", "Hello")
        serialized = protocol.serialize(msg)

        encrypted = handler.encrypt(serialized)
        decrypted = handler.decrypt(encrypted)

        assert decrypted == serialized

        # Verify we can deserialize
        msg2 = protocol.deserialize(decrypted)
        assert msg2.content == "Hello"

    def test_encryption_with_password(self):
        """Test encryption with a password-derived key."""
        handler1 = EncryptionHandler(encryption_key="my_password")
        handler2 = EncryptionHandler(encryption_key="my_password")

        message = "Secret message"
        encrypted = handler1.encrypt(message)
        decrypted = handler2.decrypt(encrypted)

        assert decrypted == message

    def test_wrong_key_fails(self):
        """Test that decryption with wrong key fails."""
        handler1 = EncryptionHandler(encryption_key="password1")
        handler2 = EncryptionHandler(encryption_key="password2")

        message = "Secret message"
        encrypted = handler1.encrypt(message)

        with pytest.raises(Exception):
            handler2.decrypt(encrypted)


# ============================================================================
# Integration Tests (require async)
# ============================================================================

@pytest.mark.asyncio
class TestAsyncIntegration:
    """Async integration tests."""

    async def test_protocol_roundtrip_async(self):
        """Test async message handling."""
        msg = create_chat_message(1, "Test", "Hello")

        # Simulate async serialization
        await asyncio.sleep(0.001)
        serialized = protocol.serialize(msg)

        # Simulate async deserialization
        await asyncio.sleep(0.001)
        deserialized = protocol.deserialize(serialized)

        assert deserialized.content == "Hello"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

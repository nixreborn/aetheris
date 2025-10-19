"""
Example usage of the Shards of Eternity networking system.

Demonstrates:
- Running a master server
- Connecting clients
- Chat communication
- Character management
- World state queries
"""
import asyncio
import logging
from typing import Optional

from network import (
    MasterServer,
    NetworkClient,
    MessageType,
    ChatMessage,
    ShardCapturedMessage,
    WorldStateMessage,
    create_client_and_connect
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Simple Client Connection
# ============================================================================

async def example_simple_client():
    """Simple example of connecting a client and sending messages."""
    print("\n=== Example 1: Simple Client ===\n")

    # Create and connect
    client = await create_client_and_connect("player1", "password123")

    if not client:
        print("Failed to connect")
        return

    try:
        # Send a chat message
        await client.send_chat("Hello from the client!")

        # Get world state
        world_state = await client.get_world_state()
        print(f"Current Reality: {world_state.get('current_reality')}")
        print(f"Active Players: {world_state.get('active_players')}")

        # Keep alive for a bit
        await asyncio.sleep(2)

    finally:
        await client.disconnect()


# ============================================================================
# Example 2: Client with Message Handlers
# ============================================================================

async def example_client_with_handlers():
    """Example client with custom message handlers."""
    print("\n=== Example 2: Client with Handlers ===\n")

    client = NetworkClient()
    await client.connect("player2", "password456")

    # Chat handler
    async def on_chat(message: ChatMessage):
        print(f"📬 [{message.channel}] {message.sender_name}: {message.content}")

    # Shard capture handler
    async def on_shard_captured(message: ShardCapturedMessage):
        print(f"💎 SHARD CAPTURED!")
        print(f"   Shard: {message.shard_name}")
        print(f"   Captured by: {message.captured_by_character_name}")
        print(f"   Faction: {message.faction}")

    # World state handler
    async def on_world_state(message: WorldStateMessage):
        print(f"🌍 World State Update")
        print(f"   Reality: {message.current_reality}")
        print(f"   Stability: {message.reality_stability}%")
        print(f"   Active Players: {message.active_players}")

    # Register handlers
    client.register_handler(MessageType.CHAT, on_chat)
    client.register_handler(MessageType.SHARD_CAPTURED, on_shard_captured)
    client.register_handler(MessageType.WORLD_STATE, on_world_state)

    try:
        # Send some messages
        await client.send_chat("Client with handlers connected!")

        # Keep alive
        await asyncio.sleep(5)

    finally:
        await client.disconnect()


# ============================================================================
# Example 3: Multiple Clients Chatting
# ============================================================================

async def example_multiple_clients():
    """Example with multiple clients communicating."""
    print("\n=== Example 3: Multiple Clients ===\n")

    # Create multiple clients
    client1 = await create_client_and_connect("alice", "password1")
    client2 = await create_client_and_connect("bob", "password2")

    if not client1 or not client2:
        print("Failed to connect clients")
        return

    # Setup chat handlers
    async def alice_chat_handler(message: ChatMessage):
        if message.sender_name != "alice":
            print(f"[Alice heard] {message.sender_name}: {message.content}")

    async def bob_chat_handler(message: ChatMessage):
        if message.sender_name != "bob":
            print(f"[Bob heard] {message.sender_name}: {message.content}")

    client1.register_handler(MessageType.CHAT, alice_chat_handler)
    client2.register_handler(MessageType.CHAT, bob_chat_handler)

    try:
        # Have them chat
        await asyncio.sleep(1)
        await client1.send_chat("Hi Bob, this is Alice!")

        await asyncio.sleep(1)
        await client2.send_chat("Hey Alice! How's the adventure going?")

        await asyncio.sleep(1)
        await client1.send_chat("Great! Just captured the Phoenix Flame shard!")

        # Let messages propagate
        await asyncio.sleep(2)

    finally:
        await client1.disconnect()
        await client2.disconnect()


# ============================================================================
# Example 4: Character Management
# ============================================================================

async def example_character_management():
    """Example of character management operations."""
    print("\n=== Example 4: Character Management ===\n")

    client = await create_client_and_connect("player3", "password789")

    if not client:
        print("Failed to connect")
        return

    try:
        # Get character list
        characters = await client.get_characters()
        print(f"Found {len(characters)} characters:")

        for char in characters:
            print(f"  - {char['name']} (Level {char['progression']['level']}, "
                  f"{char['race']} {char['class']})")

        # Select first character if available
        if characters:
            char = characters[0]
            success = await client.select_character(char['id'])

            if success:
                print(f"\nSelected character: {char['name']}")

                # Send a movement update
                await client.send_move(
                    to_location_id=1,
                    position={"x": 100.0, "y": 50.0, "z": 0.0}
                )
                print(f"Moved {char['name']} to location 1")

    finally:
        await client.disconnect()


# ============================================================================
# Example 5: World State and Shard Status
# ============================================================================

async def example_world_queries():
    """Example of querying world state and shard information."""
    print("\n=== Example 5: World Queries ===\n")

    client = await create_client_and_connect("player4", "passwordABC")

    if not client:
        print("Failed to connect")
        return

    try:
        # Get world state
        print("🌍 World State:")
        world_state = await client.get_world_state()

        print(f"  Current Reality: {world_state.get('current_reality')}")
        print(f"  Reality Stability: {world_state.get('reality_stability')}%")
        print(f"  Active Players: {world_state.get('active_players')}")
        print(f"  Total Aetherfalls: {world_state.get('total_aetherfalls')}")

        faction_counts = world_state.get('faction_shard_counts', {})
        if faction_counts:
            print("\n  Shard Distribution:")
            for faction, count in faction_counts.items():
                print(f"    {faction}: {count} shards")

        # Get shard status
        print("\n💎 Crystal Shards:")
        shards = await client.get_shard_status()

        if shards:
            for shard in shards[:5]:  # Show first 5
                status = "⚔️ CONTESTED" if not shard['is_captured'] else "✓ CAPTURED"
                owner = shard.get('owning_faction', 'None')
                print(f"  {status} {shard['name']} - Owner: {owner}")

    finally:
        await client.disconnect()


# ============================================================================
# Example 6: Party Creation and Management
# ============================================================================

async def example_party_system():
    """Example of party creation and management."""
    print("\n=== Example 6: Party System ===\n")

    leader = await create_client_and_connect("party_leader", "password")
    member = await create_client_and_connect("party_member", "password")

    if not leader or not member:
        print("Failed to connect clients")
        return

    try:
        # Get and select characters
        leader_chars = await leader.get_characters()
        member_chars = await member.get_characters()

        if leader_chars and member_chars:
            await leader.select_character(leader_chars[0]['id'])
            await member.select_character(member_chars[0]['id'])

            # Create party
            party_id = await leader.create_party("Epic Adventurers")

            if party_id:
                print(f"✓ Created party 'Epic Adventurers' (ID: {party_id})")

                # Send party chat
                await leader.send_party_chat("Welcome to the party!")

                # Let it process
                await asyncio.sleep(2)

    finally:
        await leader.disconnect()
        await member.disconnect()


# ============================================================================
# Example 7: Combat Simulation
# ============================================================================

async def example_combat():
    """Example of combat action synchronization."""
    print("\n=== Example 7: Combat Simulation ===\n")

    client = await create_client_and_connect("warrior", "password")

    if not client:
        print("Failed to connect")
        return

    try:
        chars = await client.get_characters()
        if chars:
            await client.select_character(chars[0]['id'])

            combat_id = "combat_demo_001"

            # Simulate combat actions
            print("⚔️ Starting combat simulation...")

            await client.send_combat_action(
                combat_id=combat_id,
                action_type="attack",
                target_id=999
            )
            print("  → Attacked target")
            await asyncio.sleep(1)

            await client.send_combat_action(
                combat_id=combat_id,
                action_type="spell",
                target_id=999,
                ability_name="Fireball"
            )
            print("  → Cast Fireball")
            await asyncio.sleep(1)

            await client.send_combat_action(
                combat_id=combat_id,
                action_type="item",
                item_id=123
            )
            print("  → Used health potion")

    finally:
        await client.disconnect()


# ============================================================================
# Example 8: Running the Master Server
# ============================================================================

async def example_run_server():
    """Example of running the master server."""
    print("\n=== Example 8: Running Master Server ===\n")

    server = MasterServer(host="127.0.0.1", port=8888)

    try:
        await server.start()
        print("✓ Master server started on http://127.0.0.1:8888")
        print("  - REST API available")
        print("  - WebSocket endpoint: ws://127.0.0.1:8888/ws")
        print("\nPress Ctrl+C to stop\n")

        # Keep running
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        await server.stop()


# ============================================================================
# Main Menu
# ============================================================================

async def main():
    """Run examples menu."""
    print("\n" + "="*60)
    print("  Shards of Eternity - Networking Examples")
    print("="*60)

    print("\nSelect an example to run:")
    print("  1. Simple Client Connection")
    print("  2. Client with Message Handlers")
    print("  3. Multiple Clients Chatting")
    print("  4. Character Management")
    print("  5. World State and Shard Queries")
    print("  6. Party System")
    print("  7. Combat Simulation")
    print("  8. Run Master Server")
    print("  9. Run All Examples (requires server running)")
    print("  0. Exit")

    choice = input("\nEnter choice (0-9): ").strip()

    examples = {
        "1": example_simple_client,
        "2": example_client_with_handlers,
        "3": example_multiple_clients,
        "4": example_character_management,
        "5": example_world_queries,
        "6": example_party_system,
        "7": example_combat,
        "8": example_run_server,
    }

    if choice == "9":
        # Run all client examples
        for key in ["1", "2", "3", "4", "5", "6", "7"]:
            await examples[key]()
            await asyncio.sleep(1)
    elif choice in examples:
        await examples[choice]()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")

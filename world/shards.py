"""
Crystal Shard system for Shards of Eternity.
Manages the 12 legendary Crystal Shards scattered across the world.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime
import json


class ShardElement(str, Enum):
    """Elemental affinity of each Shard."""
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHT = "light"
    DARKNESS = "darkness"
    VOID = "void"
    TIME = "time"
    SPACE = "space"
    LIFE = "life"
    DEATH = "death"
    CHAOS = "chaos"


class ShardStatus(str, Enum):
    """Current status of a Shard."""
    UNCLAIMED = "unclaimed"
    CONTESTED = "contested"
    CONTROLLED = "controlled"
    SEALED = "sealed"
    LOST = "lost"


@dataclass
class GuardianBoss:
    """Guardian protecting a Crystal Shard."""
    name: str
    level: int
    description: str
    health: int
    abilities: List[str] = field(default_factory=list)
    loot_table: Dict[str, float] = field(default_factory=dict)
    respawn_time: int = 86400  # Seconds (24 hours default)


@dataclass
class CrystalShard:
    """A single Crystal Shard with all its properties."""
    shard_id: int
    name: str
    element: ShardElement
    description: str
    lore: str

    # Location
    location_name: str
    location_id: Optional[int] = None
    coordinates: tuple[float, float, float] = (0.0, 0.0, 0.0)

    # Guardian
    guardian: Optional[GuardianBoss] = None

    # Ownership
    status: ShardStatus = ShardStatus.UNCLAIMED
    controlling_faction: Optional[str] = None
    controlling_player: Optional[str] = None
    claimed_at: Optional[datetime] = None

    # Power
    power_level: int = 100
    abilities_granted: List[str] = field(default_factory=list)

    # History
    capture_history: List[Dict] = field(default_factory=list)


class ShardManager:
    """Manages all 12 Crystal Shards and their state."""

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.shards: Dict[int, CrystalShard] = self._initialize_shards()
        self.total_shards = 12
        self.win_threshold = 12

    def _initialize_shards(self) -> Dict[int, CrystalShard]:
        """Initialize all 12 Crystal Shards with their data."""

        shards = {}

        # SHARD 1: PHOENIX FLAME
        shards[1] = CrystalShard(
            shard_id=1,
            name="Phoenix Flame",
            element=ShardElement.FIRE,
            description="A blazing crystal that burns with eternal fire",
            lore=(
                "Forged in the heart of a dying star, the Phoenix Flame has been consumed and "
                "reborn countless times across reality cycles. It grants mastery over flame and "
                "the power of resurrection. Legends say those who hold it cannot truly die."
            ),
            location_name="Ember Volcano",
            coordinates=(100.0, 50.0, 250.0),
            guardian=GuardianBoss(
                name="Ignarok the Eternal",
                level=50,
                description="An ancient fire elemental bound to protect the Phoenix Flame",
                health=50000,
                abilities=[
                    "Meteor Storm",
                    "Phoenix Resurrection",
                    "Flame Breath",
                    "Molten Armor"
                ],
                loot_table={
                    "Ember Heart": 0.1,
                    "Flame-Touched Sword": 0.25,
                    "Phoenix Feather": 0.5
                }
            ),
            abilities_granted=[
                "Fire Mastery: +50% fire damage",
                "Phoenix Rebirth: Auto-resurrect once per day",
                "Flame Cloak: Immunity to fire damage"
            ]
        )

        # SHARD 2: OCEAN'S TEAR
        shards[2] = CrystalShard(
            shard_id=2,
            name="Ocean's Tear",
            element=ShardElement.WATER,
            description="A sapphire crystal that contains the primordial ocean",
            lore=(
                "When the first ocean was born, it wept a single tear of joy. That tear crystallized "
                "into this Shard, containing the essence of all water, all emotion, all flow. "
                "It grants control over water and the ability to adapt to any situation."
            ),
            location_name="Abyssal Trench",
            coordinates=(-200.0, -500.0, 100.0),
            guardian=GuardianBoss(
                name="Thalassia the Depths",
                level=48,
                description="A colossal sea serpent older than continents",
                health=45000,
                abilities=[
                    "Tidal Wave",
                    "Whirlpool Vortex",
                    "Crushing Depths",
                    "Hydro Shield"
                ],
                loot_table={
                    "Abyssal Pearl": 0.15,
                    "Trident of Tides": 0.2,
                    "Scale of Thalassia": 0.4
                }
            ),
            abilities_granted=[
                "Water Mastery: +50% water damage",
                "Adaptive Flow: +30% resistance to all damage",
                "Oceanic Breathing: Breathe underwater, swim speed +100%"
            ]
        )

        # SHARD 3: MOUNTAIN'S CORE
        shards[3] = CrystalShard(
            shard_id=3,
            name="Mountain's Core",
            element=ShardElement.EARTH,
            description="A crystallized heart of the world's first mountain",
            lore=(
                "Before time had meaning, the first mountain rose from nothing. Its core hardened "
                "into this Shard, representing stability, endurance, and immovable will. Those "
                "who claim it become as unyielding as the earth itself."
            ),
            location_name="Titan's Spine Mountains",
            coordinates=(0.0, 0.0, 1000.0),
            guardian=GuardianBoss(
                name="Terrakor the Unmoved",
                level=55,
                description="A living mountain golem of primordial stone",
                health=75000,
                abilities=[
                    "Earthquake Slam",
                    "Boulder Barrage",
                    "Stone Prison",
                    "Tectonic Armor"
                ],
                loot_table={
                    "Core Fragment": 0.12,
                    "Earthshaker Hammer": 0.18,
                    "Titan's Blood": 0.35
                }
            ),
            abilities_granted=[
                "Earth Mastery: +50% earth damage",
                "Immovable Object: Cannot be knocked back or stunned",
                "Stone Skin: +40% physical defense"
            ]
        )

        # SHARD 4: TEMPEST CROWN
        shards[4] = CrystalShard(
            shard_id=4,
            name="Tempest Crown",
            element=ShardElement.AIR,
            description="A crystal filled with eternal storms and lightning",
            lore=(
                "In the beginning, there was chaos. The first storm separated sky from earth, "
                "and its fury crystallized into the Tempest Crown. It grants dominion over wind, "
                "weather, and lightning, as well as ultimate freedom of movement."
            ),
            location_name="Storm Citadel",
            coordinates=(300.0, 800.0, 500.0),
            guardian=GuardianBoss(
                name="Zephyrath the Hurricane",
                level=52,
                description="A sentient storm entity of pure wind and lightning",
                health=40000,
                abilities=[
                    "Lightning Chain",
                    "Tornado Summon",
                    "Wind Blade Barrage",
                    "Storm's Fury"
                ],
                loot_table={
                    "Storm Crystal": 0.15,
                    "Thunder Staff": 0.22,
                    "Essence of Wind": 0.4
                }
            ),
            abilities_granted=[
                "Air Mastery: +50% air/lightning damage",
                "Freedom of Flight: Permanent flight ability",
                "Lightning Speed: +50% movement and attack speed"
            ]
        )

        # SHARD 5: DAWN'S RADIANCE
        shards[5] = CrystalShard(
            shard_id=5,
            name="Dawn's Radiance",
            element=ShardElement.LIGHT,
            description="A brilliant crystal containing the first sunrise",
            lore=(
                "When darkness covered all, the first dawn broke and banished shadow. That moment "
                "of pure illumination became the Dawn's Radiance. It represents hope, healing, "
                "and the power to reveal all truth."
            ),
            location_name="Celestial Cathedral",
            coordinates=(400.0, 200.0, 300.0),
            guardian=GuardianBoss(
                name="Solarius the Radiant",
                level=50,
                description="A divine being of pure light and holy power",
                health=42000,
                abilities=[
                    "Divine Smite",
                    "Healing Radiance",
                    "Blinding Flash",
                    "Holy Barrier"
                ],
                loot_table={
                    "Blessed Crystal": 0.18,
                    "Radiant Sword": 0.25,
                    "Dawn Essence": 0.4
                }
            ),
            abilities_granted=[
                "Light Mastery: +50% holy/light damage",
                "Eternal Dawn: Healing spells 2x effective",
                "True Sight: See invisible, detect lies, reveal illusions"
            ]
        )

        # SHARD 6: VOID HEART
        shards[6] = CrystalShard(
            shard_id=6,
            name="Void Heart",
            element=ShardElement.DARKNESS,
            description="A black crystal that absorbs all light and hope",
            lore=(
                "Where Dawn's Radiance brought light, the Void Heart answered with darkness. "
                "It is the shadow cast by existence itself, the price of being. It grants power "
                "over shadows, fear, and the spaces between."
            ),
            location_name="Shadowfell Abyss",
            coordinates=(-400.0, -300.0, -100.0),
            guardian=GuardianBoss(
                name="Nocturnyx the Void",
                level=53,
                description="A creature that exists only as absence, as void given form",
                health=38000,
                abilities=[
                    "Void Collapse",
                    "Shadow Bind",
                    "Fear Incarnate",
                    "Dark Absorption"
                ],
                loot_table={
                    "Void Fragment": 0.1,
                    "Shadow Dagger": 0.2,
                    "Dark Essence": 0.45
                }
            ),
            abilities_granted=[
                "Darkness Mastery: +50% shadow/dark damage",
                "Shadow Walk: Become invisible in shadows, teleport between them",
                "Fear Aura: Enemies near you suffer fear debuff"
            ]
        )

        # SHARD 7: NULL SPHERE
        shards[7] = CrystalShard(
            shard_id=7,
            name="Null Sphere",
            element=ShardElement.VOID,
            description="A crystal that shouldn't exist, yet does",
            lore=(
                "The Null Sphere is the absence of reality crystallized. It exists in the space "
                "between existence and non-existence, granting power over the void and the ability "
                "to unmake creation itself. The Voidborn Cult seeks it above all others."
            ),
            location_name="Reality Rift",
            coordinates=(0.0, 0.0, 0.0),
            guardian=GuardianBoss(
                name="The Unmade",
                level=60,
                description="An entity that was erased from existence but persists as an echo",
                health=55000,
                abilities=[
                    "Reality Erasure",
                    "Void Pulse",
                    "Existence Drain",
                    "Non-Being"
                ],
                loot_table={
                    "Void Shard": 0.08,
                    "Unmade Relic": 0.15,
                    "Null Essence": 0.3
                }
            ),
            abilities_granted=[
                "Void Mastery: +50% void damage, ignore all resistances",
                "Phase Shift: Become incorporeal for short periods",
                "Unmaking Touch: Small chance to instantly destroy items/enemies"
            ]
        )

        # SHARD 8: HOURGLASS ETERNAL
        shards[8] = CrystalShard(
            shard_id=8,
            name="Hourglass Eternal",
            element=ShardElement.TIME,
            description="A crystal containing all moments simultaneously",
            lore=(
                "Time does not flowit exists all at once, and the Hourglass Eternal proves it. "
                "This Shard contains past, present, and future in crystalline suspension. Those "
                "who master it can step outside the river of time itself."
            ),
            location_name="Temporal Nexus",
            coordinates=(600.0, 100.0, 200.0),
            guardian=GuardianBoss(
                name="Chronovax the Timeless",
                level=58,
                description="A being experiencing all moments of its existence simultaneously",
                health=48000,
                abilities=[
                    "Time Stop",
                    "Age Acceleration",
                    "Temporal Rewind",
                    "Future Sight"
                ],
                loot_table={
                    "Temporal Crystal": 0.12,
                    "Timeless Blade": 0.18,
                    "Chrono Essence": 0.35
                }
            ),
            abilities_granted=[
                "Time Mastery: Slow/accelerate time in small radius",
                "Temporal Echo: Create time-displaced copies of yourself",
                "Foresight: See 10 seconds into the future constantly"
            ]
        )

        # SHARD 9: INFINITY PRISM
        shards[9] = CrystalShard(
            shard_id=9,
            name="Infinity Prism",
            element=ShardElement.SPACE,
            description="A crystal containing infinite space within finite form",
            lore=(
                "How can infinity fit in your hand? The Infinity Prism answers by containing "
                "all space within itself. Distance becomes meaningless to those who wield it, "
                "and the entire universe becomes accessible."
            ),
            location_name="Dimensional Crossroads",
            coordinates=(999.0, 999.0, 999.0),
            guardian=GuardianBoss(
                name="Infinitus the Boundless",
                level=56,
                description="A being that exists in all places simultaneously",
                health=50000,
                abilities=[
                    "Spatial Rend",
                    "Dimensional Rift",
                    "Gravity Crush",
                    "Infinite Distance"
                ],
                loot_table={
                    "Spatial Shard": 0.14,
                    "Infinity Edge": 0.2,
                    "Space Essence": 0.38
                }
            ),
            abilities_granted=[
                "Space Mastery: Teleport anywhere you've been before",
                "Dimensional Storage: Infinite inventory space",
                "Spatial Awareness: Detect all enemies within 1000m"
            ]
        )

        # SHARD 10: GENESIS SEED
        shards[10] = CrystalShard(
            shard_id=10,
            name="Genesis Seed",
            element=ShardElement.LIFE,
            description="The first spark of life crystallized",
            lore=(
                "When the universe was barren, the Genesis Seed contained the potential for all "
                "life. It is growth, healing, creation, and the unstoppable force of vitality. "
                "No death can permanently claim those protected by its power."
            ),
            location_name="Primordial Garden",
            coordinates=(250.0, 150.0, 75.0),
            guardian=GuardianBoss(
                name="Vitaera the Ever-Growing",
                level=51,
                description="An ever-evolving amalgamation of all life forms",
                health=60000,
                abilities=[
                    "Rapid Regeneration",
                    "Life Bloom",
                    "Evolution Strike",
                    "Symbiotic Defense"
                ],
                loot_table={
                    "Life Crystal": 0.16,
                    "Living Weapon": 0.22,
                    "Vital Essence": 0.42
                }
            ),
            abilities_granted=[
                "Life Mastery: +50% healing, regenerate 2% HP per second",
                "Resurrection: Revive dead allies once per hour",
                "Growth: Gain +1 to all stats permanently each week"
            ]
        )

        # SHARD 11: REAPER'S EYE
        shards[11] = CrystalShard(
            shard_id=11,
            name="Reaper's Eye",
            element=ShardElement.DEATH,
            description="A crystal containing the final breath of all things",
            lore=(
                "All things end, and the Reaper's Eye ensures it. This Shard is entropy itself, "
                "the guarantee that all stories conclude. It grants power over death, decay, "
                "and the ability to end anything permanently."
            ),
            location_name="Necropolis of Lost Souls",
            coordinates=(-350.0, -250.0, 0.0),
            guardian=GuardianBoss(
                name="Mortifax the Final",
                level=57,
                description="The embodiment of death, the ending made manifest",
                health=52000,
                abilities=[
                    "Death Touch",
                    "Soul Harvest",
                    "Necrotic Aura",
                    "Final Judgment"
                ],
                loot_table={
                    "Death Crystal": 0.11,
                    "Reaper's Scythe": 0.17,
                    "Soul Essence": 0.36
                }
            ),
            abilities_granted=[
                "Death Mastery: +50% necrotic damage, life drain on all attacks",
                "Deathless: Cannot be killed while above 1 HP",
                "Soul Reaping: Gain power from nearby deaths"
            ]
        )

        # SHARD 12: ENTROPY ENGINE
        shards[12] = CrystalShard(
            shard_id=12,
            name="Entropy Engine",
            element=ShardElement.CHAOS,
            description="Pure chaos crystallized into unstable form",
            lore=(
                "The Entropy Engine is randomness itself. It is the dice roll of fate, the "
                "unpredictable variable in every equation. Those who wield it gain immense power "
                "at tremendous risk, for chaos serves no masternot even its wielder."
            ),
            location_name="Maelstrom of Madness",
            coordinates=(-999.0, 666.0, -333.0),
            guardian=GuardianBoss(
                name="Chaoticus the Random",
                level=59,
                description="An entity of pure chaos that changes form every moment",
                health=45000,
                abilities=[
                    "Random Effect",
                    "Chaos Bolt",
                    "Reality Glitch",
                    "Unpredictable Defense"
                ],
                loot_table={
                    "Chaos Crystal": 0.13,
                    "Entropic Weapon": 0.19,
                    "Wild Essence": 0.4
                }
            ),
            abilities_granted=[
                "Chaos Mastery: All damage random between 0-200%",
                "Wild Magic: All spells have random additional effects",
                "Entropy Aura: Random effects constantly occur around you"
            ]
        )

        return shards

    def get_shard(self, shard_id: int) -> Optional[CrystalShard]:
        """Get a shard by ID."""
        return self.shards.get(shard_id)

    def get_all_shards(self) -> List[CrystalShard]:
        """Get all shards."""
        return list(self.shards.values())

    def get_shards_by_faction(self, faction_name: str) -> List[CrystalShard]:
        """Get all shards controlled by a specific faction."""
        return [
            shard for shard in self.shards.values()
            if shard.controlling_faction == faction_name
        ]

    def get_unclaimed_shards(self) -> List[CrystalShard]:
        """Get all unclaimed shards."""
        return [
            shard for shard in self.shards.values()
            if shard.status == ShardStatus.UNCLAIMED
        ]

    def capture_shard(
        self,
        shard_id: int,
        faction_name: Optional[str] = None,
        player_name: Optional[str] = None
    ) -> bool:
        """
        Attempt to capture a shard.

        Args:
            shard_id: The ID of the shard to capture
            faction_name: Name of the faction claiming it (optional)
            player_name: Name of the player claiming it (optional)

        Returns:
            True if capture successful, False otherwise
        """
        shard = self.shards.get(shard_id)
        if not shard:
            return False

        # Cannot capture sealed shards
        if shard.status == ShardStatus.SEALED:
            return False

        # Record previous owner
        previous_owner = {
            "faction": shard.controlling_faction,
            "player": shard.controlling_player,
            "released_at": datetime.now().isoformat()
        }

        # Update shard ownership
        shard.controlling_faction = faction_name
        shard.controlling_player = player_name
        shard.status = ShardStatus.CONTROLLED
        shard.claimed_at = datetime.now()

        # Add to history
        shard.capture_history.append({
            "faction": faction_name,
            "player": player_name,
            "captured_at": datetime.now().isoformat(),
            "previous_owner": previous_owner
        })

        # Persist to database if available
        if self.db_session:
            self._save_shard_to_db(shard)

        return True

    def transfer_shard(
        self,
        shard_id: int,
        new_faction: Optional[str] = None,
        new_player: Optional[str] = None
    ) -> bool:
        """Transfer shard ownership."""
        return self.capture_shard(shard_id, new_faction, new_player)

    def release_shard(self, shard_id: int) -> bool:
        """Release a shard, making it unclaimed."""
        shard = self.shards.get(shard_id)
        if not shard:
            return False

        shard.controlling_faction = None
        shard.controlling_player = None
        shard.status = ShardStatus.UNCLAIMED
        shard.claimed_at = None

        if self.db_session:
            self._save_shard_to_db(shard)

        return True

    def seal_shard(self, shard_id: int, duration: Optional[int] = None) -> bool:
        """
        Seal a shard, preventing it from being captured.
        Used by Eternal Wardens faction ability.
        """
        shard = self.shards.get(shard_id)
        if not shard:
            return False

        shard.status = ShardStatus.SEALED
        # TODO: Implement timed unsealing if duration provided

        if self.db_session:
            self._save_shard_to_db(shard)

        return True

    def unseal_shard(self, shard_id: int) -> bool:
        """Unseal a shard."""
        shard = self.shards.get(shard_id)
        if not shard:
            return False

        if shard.status == ShardStatus.SEALED:
            shard.status = ShardStatus.UNCLAIMED

        if self.db_session:
            self._save_shard_to_db(shard)

        return True

    def check_victory(self, faction_name: str) -> bool:
        """Check if a faction has won by controlling all 12 shards."""
        faction_shards = self.get_shards_by_faction(faction_name)
        return len(faction_shards) >= self.win_threshold

    def get_faction_shard_count(self, faction_name: str) -> int:
        """Get the number of shards controlled by a faction."""
        return len(self.get_shards_by_faction(faction_name))

    def get_shard_distribution(self) -> Dict[str, int]:
        """Get distribution of shards across all factions."""
        distribution = {}
        for shard in self.shards.values():
            if shard.controlling_faction:
                faction = shard.controlling_faction
                distribution[faction] = distribution.get(faction, 0) + 1
        return distribution

    def get_shard_by_location(self, location_name: str) -> Optional[CrystalShard]:
        """Get a shard by its location name."""
        for shard in self.shards.values():
            if shard.location_name.lower() == location_name.lower():
                return shard
        return None

    def get_shards_by_element(self, element: ShardElement) -> List[CrystalShard]:
        """Get all shards of a specific element."""
        return [
            shard for shard in self.shards.values()
            if shard.element == element
        ]

    def _save_shard_to_db(self, shard: CrystalShard):
        """Save shard state to database."""
        if not self.db_session:
            return

        try:
            from database.models import GameState

            # Store shard data as JSON in game_state table
            shard_data = {
                "controlling_faction": shard.controlling_faction,
                "controlling_player": shard.controlling_player,
                "status": shard.status.value,
                "claimed_at": shard.claimed_at.isoformat() if shard.claimed_at else None,
                "power_level": shard.power_level,
                "capture_history": shard.capture_history
            }

            key = f"shard_{shard.shard_id}"
            state = self.db_session.query(GameState).filter_by(key=key).first()

            if state:
                state.value = json.dumps(shard_data)
                state.value_type = "json"
            else:
                state = GameState(
                    key=key,
                    value=json.dumps(shard_data),
                    value_type="json"
                )
                self.db_session.add(state)

            self.db_session.commit()
        except Exception as e:
            print(f"Error saving shard to database: {e}")
            self.db_session.rollback()

    def load_shard_states_from_db(self):
        """Load shard states from database."""
        if not self.db_session:
            return

        try:
            from database.models import GameState

            for shard_id in range(1, 13):
                key = f"shard_{shard_id}"
                state = self.db_session.query(GameState).filter_by(key=key).first()

                if state and state.value_type == "json":
                    data = json.loads(state.value)
                    shard = self.shards.get(shard_id)

                    if shard:
                        shard.controlling_faction = data.get("controlling_faction")
                        shard.controlling_player = data.get("controlling_player")
                        shard.status = ShardStatus(data.get("status", "unclaimed"))
                        shard.power_level = data.get("power_level", 100)
                        shard.capture_history = data.get("capture_history", [])

                        claimed_at = data.get("claimed_at")
                        if claimed_at:
                            shard.claimed_at = datetime.fromisoformat(claimed_at)

        except Exception as e:
            print(f"Error loading shards from database: {e}")

    def reset_all_shards(self):
        """Reset all shards to unclaimed state (for Aetherfall)."""
        for shard in self.shards.values():
            shard.controlling_faction = None
            shard.controlling_player = None
            shard.status = ShardStatus.UNCLAIMED
            shard.claimed_at = None
            # Keep capture history for lore purposes

        if self.db_session:
            for shard in self.shards.values():
                self._save_shard_to_db(shard)

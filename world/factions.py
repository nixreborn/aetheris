"""
Faction system for Shards of Eternity.
Defines the 6 major factions competing for the Crystal Shards and control over reality.
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field


class FactionType(str, Enum):
    """The six major factions in Shards of Eternity."""
    SEEKERS = "Seekers of Truth"
    SHAPERS = "Reality Shapers"
    WARDENS = "Eternal Wardens"
    VOIDBORN = "Voidborn Cult"
    MERCHANTS = "Merchant Concordat"
    FREELANCE = "Freelance Operatives"


class Relationship(str, Enum):
    """Faction relationship states."""
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    UNFRIENDLY = "unfriendly"
    HOSTILE = "hostile"
    ENEMIES = "enemies"


@dataclass
class FactionAbility:
    """A unique faction ability or bonus."""
    name: str
    description: str
    effect: str
    cooldown: Optional[int] = None  # In game ticks/turns


@dataclass
class VictoryCondition:
    """What happens when this faction wins Aetherfall."""
    name: str
    description: str
    reality_changes: Dict[str, any] = field(default_factory=dict)
    world_effects: List[str] = field(default_factory=list)


@dataclass
class Faction:
    """Complete faction definition."""
    faction_type: FactionType
    name: str
    description: str
    lore: str
    philosophy: str

    # Faction mechanics
    abilities: List[FactionAbility] = field(default_factory=list)
    victory_condition: Optional[VictoryCondition] = None
    relationships: Dict[FactionType, Relationship] = field(default_factory=dict)

    # Faction stats
    influence: int = 0
    shards_controlled: int = 0
    member_count: int = 0

    # Colors and symbols for UI
    primary_color: str = "#FFFFFF"
    symbol: str = ""


class FactionManager:
    """Manages all factions and their relationships."""

    def __init__(self):
        self.factions: Dict[FactionType, Faction] = self._initialize_factions()

    def _initialize_factions(self) -> Dict[FactionType, Faction]:
        """Initialize all six factions with their complete data."""

        # ===== SEEKERS OF TRUTH =====
        seekers = Faction(
            faction_type=FactionType.SEEKERS,
            name="Seekers of Truth",
            description="Ancient scholars dedicated to understanding the true nature of reality",
            lore=(
                "Founded in the First Cycle by the Sage-King Alareth, the Seekers of Truth are "
                "the oldest continuous organization in the known world. They believe the Crystal "
                "Shards are fragments of a primordial consciousness, and that gathering them will "
                "reveal the ultimate truth of existence. Their libraries contain records spanning "
                "hundreds of reality cycles, making them the keepers of dangerous knowledge."
            ),
            philosophy=(
                "Knowledge is the only constant across realities. Truth transcends cycles. "
                "To understand is to control. The Shards are not weapons, but keys to enlightenment."
            ),
            abilities=[
                FactionAbility(
                    name="Recall Past Cycles",
                    description="Draw upon ancient knowledge from previous reality cycles",
                    effect="+20% XP gain, can sometimes glimpse future events",
                    cooldown=100
                ),
                FactionAbility(
                    name="Shard Resonance",
                    description="Better understanding of Shard powers",
                    effect="20% increased shard fragment drops, +10% shard power effectiveness"
                ),
                FactionAbility(
                    name="Arcane Research",
                    description="Enhanced magical learning",
                    effect="+15% spell damage, faster spell learning"
                )
            ],
            victory_condition=VictoryCondition(
                name="The Great Revelation",
                description=(
                    "The Seekers unlock the fundamental truth of reality itself. The cycle of "
                    "Aetherfall ends, replaced by stable enlightened existence where knowledge "
                    "is shared freely across all dimensions."
                ),
                reality_changes={
                    "magic_power": 1.5,
                    "knowledge_accessible": True,
                    "reality_stable": True,
                    "aetherfall_cycle": "ended"
                },
                world_effects=[
                    "All players gain access to Seeker knowledge libraries",
                    "Magic becomes more powerful but more stable",
                    "Ancient ruins reveal their secrets",
                    "New scholarly quests and research opportunities appear",
                    "The Veil between dimensions becomes transparent"
                ]
            ),
            relationships={
                FactionType.SHAPERS: Relationship.UNFRIENDLY,
                FactionType.WARDENS: Relationship.FRIENDLY,
                FactionType.VOIDBORN: Relationship.HOSTILE,
                FactionType.MERCHANTS: Relationship.NEUTRAL,
                FactionType.FREELANCE: Relationship.NEUTRAL
            },
            primary_color="#4A90E2",  # Scholarly blue
            symbol="[BOOK]"
        )

        # ===== REALITY SHAPERS =====
        shapers = Faction(
            faction_type=FactionType.SHAPERS,
            name="Reality Shapers",
            description="Ambitious mages who seek to become gods by mastering the Shards",
            lore=(
                "The Reality Shapers emerged from a schism within the Seekers three cycles ago. "
                "Led by the enigmatic Archmagus Velthara, they believe the Shards are tools of "
                "creation, meant to be wielded by those with the vision and will to reshape "
                "existence itself. Where the Seekers seek to understand, the Shapers seek to "
                "control. They have demonstrated terrifying mastery over reality manipulation, "
                "but at great cost to themselves and the world."
            ),
            philosophy=(
                "Reality is clay in the hands of those bold enough to shape it. The Shards are "
                "not mysteries to solve, but tools to master. Power is the only truth. "
                "Become the god your world needs."
            ),
            abilities=[
                FactionAbility(
                    name="Reality Warp",
                    description="Temporarily alter the laws of physics in your vicinity",
                    effect="Can break normal game rules briefly (walk through walls, fly, etc)",
                    cooldown=200
                ),
                FactionAbility(
                    name="Shard Mastery",
                    description="Enhanced control over Shard powers",
                    effect="+25% damage when using Shard powers, reduced mana cost",
                ),
                FactionAbility(
                    name="Transmutation",
                    description="Convert materials and energy",
                    effect="Can convert low-tier items to higher tiers, transmute elements"
                )
            ],
            victory_condition=VictoryCondition(
                name="Ascension Protocol",
                description=(
                    "The Reality Shapers transcend mortality, becoming god-like entities. "
                    "Reality becomes fluid and chaotic, shaped by the whims of powerful mages. "
                    "Magic reigns supreme, but at the cost of stability and natural law."
                ),
                reality_changes={
                    "magic_power": 2.0,
                    "reality_stable": False,
                    "physics_consistent": False,
                    "shaper_ascended": True
                },
                world_effects=[
                    "Wild magic zones appear randomly throughout the world",
                    "Gravity, time, and space become unpredictable",
                    "Powerful transmutation becomes available to all mages",
                    "Non-magical classes struggle in the new reality",
                    "Pocket dimensions and floating islands appear"
                ]
            ),
            relationships={
                FactionType.SEEKERS: Relationship.UNFRIENDLY,
                FactionType.WARDENS: Relationship.HOSTILE,
                FactionType.VOIDBORN: Relationship.NEUTRAL,
                FactionType.MERCHANTS: Relationship.FRIENDLY,
                FactionType.FREELANCE: Relationship.NEUTRAL
            },
            primary_color="#9B59B6",  # Arcane purple
            symbol="[ORB]"
        )

        # ===== ETERNAL WARDENS =====
        wardens = Faction(
            faction_type=FactionType.WARDENS,
            name="Eternal Wardens",
            description="Protectors sworn to prevent any faction from claiming all Shards",
            lore=(
                "The Eternal Wardens are not a traditional faction but a sacred order spanning "
                "multiple races and species. They remember the catastrophe of the Zero Cycle, "
                "when the Shards were first united, triggering an endless chain of reality "
                "collapses. The Wardens believe the Shards must remain separate, guarded but "
                "never unified. They are the only faction that doesn't seek to win Aetherfall, "
                "but to prevent it entirely. Many consider them noble guardians; others see "
                "them as obstacles to progress."
            ),
            philosophy=(
                "Some powers should never be claimed. The Shards are a curse, not a blessing. "
                "Eternal vigilance protects all existence. Sacrifice today for tomorrow's survival. "
                "We are the shield against oblivion."
            ),
            abilities=[
                FactionAbility(
                    name="Guardian's Resolve",
                    description="Unbreakable determination in defense",
                    effect="+30% defense, +20% health when protecting a Shard location"
                ),
                FactionAbility(
                    name="Shard Seal",
                    description="Temporarily lock a Shard from being claimed",
                    effect="Prevent Shard capture for 50 turns",
                    cooldown=500
                ),
                FactionAbility(
                    name="Warden's Oath",
                    description="Divine protection for selfless acts",
                    effect="Damage reflection, auto-revive once per day"
                )
            ],
            victory_condition=VictoryCondition(
                name="Eternal Equilibrium",
                description=(
                    "The Wardens successfully scatter and seal all 12 Shards across impossible-to-reach "
                    "dimensions. The cycle of Aetherfall slows dramatically, giving civilization "
                    "centuries of stable peace. However, stagnation begins to set in, and progress "
                    "halts as the world becomes locked in endless preservation."
                ),
                reality_changes={
                    "aetherfall_cycle": "delayed",
                    "shard_accessibility": "sealed",
                    "reality_stable": True,
                    "progress_rate": 0.5
                },
                world_effects=[
                    "Aetherfall timer extended by 1000x",
                    "All Shards become inaccessible",
                    "World enters an age of peace but stagnation",
                    "No major changes occur for centuries",
                    "Warden citadels become centers of civilization"
                ]
            ),
            relationships={
                FactionType.SEEKERS: Relationship.FRIENDLY,
                FactionType.SHAPERS: Relationship.HOSTILE,
                FactionType.VOIDBORN: Relationship.ENEMIES,
                FactionType.MERCHANTS: Relationship.NEUTRAL,
                FactionType.FREELANCE: Relationship.NEUTRAL
            },
            primary_color="#27AE60",  # Guardian green
            symbol="[SHIELD]"
        )

        # ===== VOIDBORN CULT =====
        voidborn = Faction(
            faction_type=FactionType.VOIDBORN,
            name="Voidborn Cult",
            description="Nihilistic cultists who worship the void between realities",
            lore=(
                "The Voidborn Cult is the youngest faction, emerging only two cycles ago when "
                "a group of reality-displaced individuals discovered the spaces between worlds. "
                "They believe that true existence lies not in reality, but in the infinite void "
                "that surrounds and connects all realities. Their leader, known only as the "
                "Hollow Prophet, claims the Shards are chains binding reality to a false existence. "
                "By claiming all Shards and casting them into the void, they believe they can "
                "free all consciousness from the prison of physical form."
            ),
            philosophy=(
                "Form is illusion. Matter is suffering. The void is peace. Reality is a prison "
                "from which we must escape. Embrace the nothing, become the nothing, free the nothing."
            ),
            abilities=[
                FactionAbility(
                    name="Void Step",
                    description="Phase through reality itself",
                    effect="Teleport short distances, pass through barriers",
                    cooldown=50
                ),
                FactionAbility(
                    name="Entropy Touch",
                    description="Accelerate decay and dissolution",
                    effect="+25% damage to constructs, armor, and shields; bypass resistances"
                ),
                FactionAbility(
                    name="Hollow Blessing",
                    description="Embrace the void within",
                    effect="Take reduced damage by becoming partially non-corporeal (-30% damage taken)"
                )
            ],
            victory_condition=VictoryCondition(
                name="The Great Unmaking",
                description=(
                    "The Voidborn successfully cast all 12 Shards into the void between realities. "
                    "The barriers separating existence from non-existence begin to dissolve. "
                    "Reality itself starts to unravel, with entire regions flickering in and out "
                    "of existence. Whether this is transcendence or annihilation remains unclear."
                ),
                reality_changes={
                    "reality_stable": False,
                    "void_incursion": True,
                    "existence_certainty": 0.5,
                    "shards_location": "void"
                },
                world_effects=[
                    "Random regions phase out of existence temporarily",
                    "Void portals open throughout the world",
                    "Players can access the void realm",
                    "NPCs and creatures begin disappearing",
                    "Physics becomes extremely unreliable",
                    "New void-touched enemies and items appear"
                ]
            ),
            relationships={
                FactionType.SEEKERS: Relationship.HOSTILE,
                FactionType.SHAPERS: Relationship.NEUTRAL,
                FactionType.WARDENS: Relationship.ENEMIES,
                FactionType.MERCHANTS: Relationship.UNFRIENDLY,
                FactionType.FREELANCE: Relationship.UNFRIENDLY
            },
            primary_color="#34495E",  # Void dark
            symbol="[VOID]"
        )

        # ===== MERCHANT CONCORDAT =====
        merchants = Faction(
            faction_type=FactionType.MERCHANTS,
            name="Merchant Concordat",
            description="Pragmatic traders who see the Shards as the ultimate commodity",
            lore=(
                "The Merchant Concordat is not driven by ideology or mysticism, but pure pragmatism. "
                "They recognize that whoever controls the Shards controls reality itself, making "
                "them the ultimate monopoly. Led by the Council of Golden Voices, the Concordat "
                "seeks to acquire all Shards not to use them, but to broker their power. In their "
                "vision, the Shards become a service economy where reality itself can be bought, "
                "sold, and rented. Morality is irrelevant; profit is eternal."
            ),
            philosophy=(
                "Everything has a price, including reality itself. Power flows to those who "
                "control resources. The Shards are the ultimate asset. In the end, all factions "
                "will come to the negotiating table."
            ),
            abilities=[
                FactionAbility(
                    name="Gold Rush",
                    description="Enhanced wealth generation",
                    effect="+50% gold from all sources, better loot drops"
                ),
                FactionAbility(
                    name="Market Manipulation",
                    description="Control prices and availability",
                    effect="Can buy rare items, sell items for more, access black markets"
                ),
                FactionAbility(
                    name="Mercenary Contract",
                    description="Hire powerful NPCs to fight for you",
                    effect="Summon NPC mercenaries to aid in combat",
                    cooldown=150
                )
            ],
            victory_condition=VictoryCondition(
                name="The Eternal Market",
                description=(
                    "The Merchant Concordat monetizes reality itself. The Shards become the backing "
                    "for a universal currency that spans all dimensions. Everything, from physics "
                    "to time to life itself, can be bought and sold. Wealth becomes the ultimate "
                    "power, and the Concordat sits at the center of all transactions."
                ),
                reality_changes={
                    "economy_based_reality": True,
                    "wealth_equals_power": True,
                    "universal_currency": "shard_credits",
                    "free_will": "negotiable"
                },
                world_effects=[
                    "All actions require payment (including basic movement)",
                    "Wealth determines health, power, and abilities",
                    "Markets appear everywhere, even in dungeons",
                    "NPCs can be permanently purchased",
                    "Time itself can be bought and sold",
                    "Extreme wealth inequality becomes reality-defining"
                ]
            ),
            relationships={
                FactionType.SEEKERS: Relationship.NEUTRAL,
                FactionType.SHAPERS: Relationship.FRIENDLY,
                FactionType.WARDENS: Relationship.NEUTRAL,
                FactionType.VOIDBORN: Relationship.UNFRIENDLY,
                FactionType.FREELANCE: Relationship.ALLIED
            },
            primary_color="#F39C12",  # Gold
            symbol="[GOLD]"
        )

        # ===== FREELANCE OPERATIVES =====
        freelance = Faction(
            faction_type=FactionType.FREELANCE,
            name="Freelance Operatives",
            description="Independent agents loyal only to themselves and their allies",
            lore=(
                "Not everyone fits into the grand schemes of the major factions. The Freelance "
                "Operatives are a loose network of independent adventurers, mercenaries, and "
                "rogues who pursue the Shards for personal reasons. Some seek power, others "
                "wealth, still others revenge or redemption. What unites them is their refusal "
                "to be bound by faction doctrine. They are wildcards in the great game, capable "
                "of shifting allegiances or going solo when it suits them."
            ),
            philosophy=(
                "No masters, no chains. Choose your own path. Loyalty is earned, not demanded. "
                "The Shards belong to whoever can claim them. Freedom above all else."
            ),
            abilities=[
                FactionAbility(
                    name="Free Agent",
                    description="Work with any faction temporarily",
                    effect="Can accept quests from all factions, gain temporary faction bonuses"
                ),
                FactionAbility(
                    name="Solo Expertise",
                    description="Enhanced abilities when working alone",
                    effect="+20% all stats when not in a party"
                ),
                FactionAbility(
                    name="Adaptability",
                    description="Learn and adapt quickly",
                    effect="Can learn abilities from any class, faster skill progression"
                )
            ],
            victory_condition=VictoryCondition(
                name="Era of Individuals",
                description=(
                    "A Freelance operative claims all 12 Shards but refuses to use them for any "
                    "grand scheme. Instead, they fragment and distribute the Shards' power to "
                    "individuals across the world. Reality becomes a meritocracy where personal "
                    "power and choice reign supreme. No gods, no masters, only the will of free beings."
                ),
                reality_changes={
                    "power_distribution": "individual",
                    "faction_authority": False,
                    "personal_agency": 2.0,
                    "chaos_level": "high"
                },
                world_effects=[
                    "All players gain minor Shard powers",
                    "Faction structures collapse",
                    "World becomes extremely chaotic but free",
                    "Personal choices have massive consequences",
                    "New heroes and villains emerge constantly",
                    "No central authority or order exists"
                ]
            ),
            relationships={
                FactionType.SEEKERS: Relationship.NEUTRAL,
                FactionType.SHAPERS: Relationship.NEUTRAL,
                FactionType.WARDENS: Relationship.NEUTRAL,
                FactionType.VOIDBORN: Relationship.UNFRIENDLY,
                FactionType.MERCHANTS: Relationship.ALLIED
            },
            primary_color="#95A5A6",  # Independent gray
            symbol="[SWORD]"
        )

        return {
            FactionType.SEEKERS: seekers,
            FactionType.SHAPERS: shapers,
            FactionType.WARDENS: wardens,
            FactionType.VOIDBORN: voidborn,
            FactionType.MERCHANTS: merchants,
            FactionType.FREELANCE: freelance
        }

    def get_faction(self, faction_type: FactionType) -> Faction:
        """Get a faction by type."""
        return self.factions[faction_type]

    def get_all_factions(self) -> List[Faction]:
        """Get all factions."""
        return list(self.factions.values())

    def get_relationship(self, faction1: FactionType, faction2: FactionType) -> Relationship:
        """Get the relationship between two factions."""
        if faction1 == faction2:
            return Relationship.ALLIED

        faction = self.factions[faction1]
        return faction.relationships.get(faction2, Relationship.NEUTRAL)

    def update_shard_count(self, faction_type: FactionType, count: int):
        """Update the number of shards controlled by a faction."""
        self.factions[faction_type].shards_controlled = count

    def add_member(self, faction_type: FactionType):
        """Add a member to a faction."""
        self.factions[faction_type].member_count += 1

    def remove_member(self, faction_type: FactionType):
        """Remove a member from a faction."""
        if self.factions[faction_type].member_count > 0:
            self.factions[faction_type].member_count -= 1

    def modify_influence(self, faction_type: FactionType, amount: int):
        """Modify a faction's influence score."""
        self.factions[faction_type].influence += amount
        self.factions[faction_type].influence = max(0, self.factions[faction_type].influence)

    def get_winning_faction(self) -> Optional[Faction]:
        """Get the faction that has won (12 shards), if any."""
        for faction in self.factions.values():
            if faction.shards_controlled >= 12:
                return faction
        return None

    def get_faction_by_name(self, name: str) -> Optional[Faction]:
        """Get a faction by its display name."""
        for faction in self.factions.values():
            if faction.name.lower() == name.lower():
                return faction
        return None

    def get_leaderboard(self) -> List[Faction]:
        """Get factions ranked by shards controlled and influence."""
        return sorted(
            self.factions.values(),
            key=lambda f: (f.shards_controlled, f.influence),
            reverse=True
        )

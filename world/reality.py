"""
Reality system for Shards of Eternity.
Manages Aetherfall (world resets) and reality transformations.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json
import random


class RealityState(str, Enum):
    """Possible states of reality."""
    STABLE = "stable"
    UNSTABLE = "unstable"
    FRAGMENTING = "fragmenting"
    COLLAPSING = "collapsing"
    RESETTING = "resetting"
    TRANSFORMED = "transformed"


class TransformationType(str, Enum):
    """Types of reality transformations."""
    ENEMY_MUTATION = "enemy_mutation"
    ENVIRONMENT_SHIFT = "environment_shift"
    PHYSICS_ALTERATION = "physics_alteration"
    TIMELINE_DIVERGENCE = "timeline_divergence"
    DIMENSIONAL_MERGE = "dimensional_merge"
    ELEMENTAL_DOMINANCE = "elemental_dominance"


@dataclass
class RealityTransformation:
    """A transformation applied to reality."""
    transformation_type: TransformationType
    name: str
    description: str
    effects: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[int] = None  # None = permanent until Aetherfall
    applied_at: Optional[datetime] = None


@dataclass
class AetherfallEvent:
    """Record of an Aetherfall (world reset) event."""
    cycle_number: int
    triggered_at: datetime
    winning_faction: Optional[str] = None
    reality_changes: Dict[str, Any] = field(default_factory=dict)
    survivors: List[str] = field(default_factory=list)
    transformations_applied: List[str] = field(default_factory=list)


class RealityManager:
    """Manages the state of reality and Aetherfall events."""

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.current_cycle = 0
        self.reality_state = RealityState.STABLE
        self.active_transformations: List[RealityTransformation] = []
        self.aetherfall_history: List[AetherfallEvent] = []
        self.reality_stability = 100.0  # 0-100, lower = more unstable

        # Load saved state from database
        if db_session:
            self.load_state_from_db()

    def trigger_aetherfall(
        self,
        winning_faction: Optional[str] = None,
        faction_victory_condition: Optional[Dict] = None
    ) -> AetherfallEvent:
        """
        Trigger Aetherfall - the world reset event.

        This happens when:
        1. A faction claims all 12 shards
        2. Reality stability drops to 0
        3. Manually triggered by admin

        Args:
            winning_faction: Name of the faction that won (if any)
            faction_victory_condition: The victory condition data from the winning faction

        Returns:
            AetherfallEvent record
        """
        self.reality_state = RealityState.COLLAPSING

        # Create event record
        event = AetherfallEvent(
            cycle_number=self.current_cycle + 1,
            triggered_at=datetime.now(),
            winning_faction=winning_faction
        )

        # Apply faction-specific reality changes if there's a winner
        if winning_faction and faction_victory_condition:
            reality_changes = faction_victory_condition.get("reality_changes", {})
            world_effects = faction_victory_condition.get("world_effects", [])

            event.reality_changes = reality_changes
            event.transformations_applied = world_effects

            # Apply the transformations
            self._apply_faction_victory(winning_faction, faction_victory_condition)

        else:
            # No clear winner - random transformations
            self._apply_random_transformations(event)

        # Reset world state
        self._reset_world(event)

        # Increment cycle
        self.current_cycle += 1
        self.reality_state = RealityState.STABLE
        self.reality_stability = 100.0

        # Store event
        self.aetherfall_history.append(event)

        # Save to database
        if self.db_session:
            self.save_state_to_db()

        return event

    def _apply_faction_victory(
        self,
        faction_name: str,
        victory_condition: Dict
    ):
        """Apply the specific reality transformations of a winning faction."""
        reality_changes = victory_condition.get("reality_changes", {})
        world_effects = victory_condition.get("world_effects", [])

        # Create transformations based on faction victory
        if faction_name == "Seekers of Truth":
            self._apply_seekers_victory(reality_changes)
        elif faction_name == "Reality Shapers":
            self._apply_shapers_victory(reality_changes)
        elif faction_name == "Eternal Wardens":
            self._apply_wardens_victory(reality_changes)
        elif faction_name == "Voidborn Cult":
            self._apply_voidborn_victory(reality_changes)
        elif faction_name == "Merchant Concordat":
            self._apply_merchants_victory(reality_changes)
        elif faction_name == "Freelance Operatives":
            self._apply_freelance_victory(reality_changes)

    def _apply_seekers_victory(self, changes: Dict):
        """Apply Seekers of Truth victory transformations."""
        # Magic becomes more powerful and stable
        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.PHYSICS_ALTERATION,
            name="Age of Enlightenment",
            description="Magic flows freely, knowledge is accessible to all",
            effects={
                "magic_power_multiplier": 1.5,
                "spell_stability": "increased",
                "knowledge_availability": "universal",
                "ancient_ruins": "revealed"
            },
            applied_at=datetime.now()
        ))

    def _apply_shapers_victory(self, changes: Dict):
        """Apply Reality Shapers victory transformations."""
        # Reality becomes chaotic and fluid
        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.PHYSICS_ALTERATION,
            name="Reality Flux",
            description="The laws of physics become suggestions",
            effects={
                "magic_power_multiplier": 2.0,
                "physics_consistency": "variable",
                "wild_magic_zones": "abundant",
                "reality_stability": "low"
            },
            applied_at=datetime.now()
        ))

        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.ENVIRONMENT_SHIFT,
            name="Floating Islands",
            description="Landmasses detach and float freely",
            effects={
                "gravity": "optional",
                "floating_zones": True,
                "pocket_dimensions": "accessible"
            },
            applied_at=datetime.now()
        ))

    def _apply_wardens_victory(self, changes: Dict):
        """Apply Eternal Wardens victory transformations."""
        # World becomes extremely stable but stagnant
        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.TIMELINE_DIVERGENCE,
            name="Eternal Peace",
            description="Progress stops, but so does conflict",
            effects={
                "aetherfall_timer_multiplier": 1000,
                "conflict_level": "minimal",
                "innovation_rate": 0.5,
                "stability": "maximum"
            },
            applied_at=datetime.now()
        ))

    def _apply_voidborn_victory(self, changes: Dict):
        """Apply Voidborn Cult victory transformations."""
        # Reality begins dissolving into void
        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.DIMENSIONAL_MERGE,
            name="Void Incursion",
            description="The void bleeds into reality",
            effects={
                "void_portals": "everywhere",
                "existence_stability": 0.5,
                "phasing_zones": "random",
                "void_creatures": "abundant"
            },
            applied_at=datetime.now()
        ))

        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.PHYSICS_ALTERATION,
            name="Reality Dissolution",
            description="Matter becomes uncertain",
            effects={
                "corporeal_stability": "variable",
                "random_phasing": True,
                "void_accessibility": "unrestricted"
            },
            applied_at=datetime.now()
        ))

    def _apply_merchants_victory(self, changes: Dict):
        """Apply Merchant Concordat victory transformations."""
        # Everything becomes commoditized
        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.PHYSICS_ALTERATION,
            name="Universal Market",
            description="All things have a price, including reality itself",
            effects={
                "economy_based_physics": True,
                "wealth_power_correlation": "direct",
                "markets": "omnipresent",
                "time_tradeable": True
            },
            applied_at=datetime.now()
        ))

    def _apply_freelance_victory(self, changes: Dict):
        """Apply Freelance Operatives victory transformations."""
        # Power distributes to individuals
        self.apply_transformation(RealityTransformation(
            transformation_type=TransformationType.PHYSICS_ALTERATION,
            name="Age of Individuals",
            description="Personal power reigns supreme",
            effects={
                "individual_empowerment": True,
                "faction_structures": "collapsed",
                "chaos_level": "high",
                "personal_agency": 2.0
            },
            applied_at=datetime.now()
        ))

    def _apply_random_transformations(self, event: AetherfallEvent):
        """Apply random transformations when no faction wins clearly."""
        num_transformations = random.randint(2, 5)

        possible_transformations = [
            RealityTransformation(
                transformation_type=TransformationType.ENEMY_MUTATION,
                name="Corrupted Evolution",
                description="Creatures mutate into twisted forms",
                effects={
                    "enemy_health_multiplier": 1.3,
                    "enemy_abilities": "enhanced",
                    "mutation_rate": "high"
                }
            ),
            RealityTransformation(
                transformation_type=TransformationType.ENVIRONMENT_SHIFT,
                name="Biome Chaos",
                description="Climate zones shift and merge unpredictably",
                effects={
                    "biome_stability": "none",
                    "weather_patterns": "chaotic",
                    "temperature_range": "extreme"
                }
            ),
            RealityTransformation(
                transformation_type=TransformationType.ELEMENTAL_DOMINANCE,
                name="Elemental Surge",
                description="One element dominates all others",
                effects={
                    "dominant_element": random.choice(["fire", "water", "earth", "air"]),
                    "element_power": 2.0,
                    "opposing_element": 0.5
                }
            ),
            RealityTransformation(
                transformation_type=TransformationType.PHYSICS_ALTERATION,
                name="Gravity Anomaly",
                description="Gravity behaves unpredictably",
                effects={
                    "gravity_consistency": "variable",
                    "falling_damage": "random",
                    "flight_difficulty": "variable"
                }
            ),
            RealityTransformation(
                transformation_type=TransformationType.TIMELINE_DIVERGENCE,
                name="Temporal Echo",
                description="Past events ripple into the present",
                effects={
                    "historical_entities": "appearing",
                    "timeline_stability": "low",
                    "paradoxes": "possible"
                }
            )
        ]

        selected = random.sample(possible_transformations, num_transformations)
        for transformation in selected:
            transformation.applied_at = datetime.now()
            self.apply_transformation(transformation)
            event.transformations_applied.append(transformation.name)

    def _reset_world(self, event: AetherfallEvent):
        """Reset world state while preserving some elements."""
        # This would:
        # 1. Reset all shard ownership (handled by ShardManager)
        # 2. Reset character positions (with some exceptions)
        # 3. Regenerate dungeons and loot
        # 4. Reset faction influence
        # 5. Apply new transformations

        # Players who are in "safe zones" during Aetherfall survive with memories
        # This is game-specific logic that would integrate with character system
        pass

    def apply_transformation(self, transformation: RealityTransformation):
        """Apply a reality transformation."""
        self.active_transformations.append(transformation)

        # Transformations affect stability
        self.reality_stability -= random.uniform(5, 15)
        self.reality_stability = max(0, self.reality_stability)

        if self.reality_stability < 30:
            self.reality_state = RealityState.UNSTABLE
        elif self.reality_stability < 15:
            self.reality_state = RealityState.FRAGMENTING

        if self.db_session:
            self.save_state_to_db()

    def remove_transformation(self, transformation_name: str) -> bool:
        """Remove an active transformation."""
        for i, trans in enumerate(self.active_transformations):
            if trans.name == transformation_name:
                self.active_transformations.pop(i)
                self.reality_stability += 10
                self.reality_stability = min(100, self.reality_stability)

                if self.db_session:
                    self.save_state_to_db()
                return True
        return False

    def get_active_transformations(self) -> List[RealityTransformation]:
        """Get all currently active transformations."""
        return self.active_transformations.copy()

    def degrade_stability(self, amount: float = 1.0):
        """Degrade reality stability (happens over time, during conflicts, etc)."""
        self.reality_stability -= amount
        self.reality_stability = max(0, self.reality_stability)

        # Update state based on stability
        if self.reality_stability <= 0:
            self.reality_state = RealityState.COLLAPSING
            # Could auto-trigger Aetherfall here
        elif self.reality_stability < 15:
            self.reality_state = RealityState.FRAGMENTING
        elif self.reality_stability < 30:
            self.reality_state = RealityState.UNSTABLE
        else:
            self.reality_state = RealityState.STABLE

        if self.db_session:
            self.save_state_to_db()

    def restore_stability(self, amount: float = 1.0):
        """Restore reality stability."""
        self.reality_stability += amount
        self.reality_stability = min(100, self.reality_stability)

        # Update state
        if self.reality_stability >= 30:
            self.reality_state = RealityState.STABLE

        if self.db_session:
            self.save_state_to_db()

    def get_reality_status(self) -> Dict[str, Any]:
        """Get current reality status information."""
        return {
            "cycle": self.current_cycle,
            "state": self.reality_state.value,
            "stability": self.reality_stability,
            "active_transformations": len(self.active_transformations),
            "transformations": [
                {
                    "name": t.name,
                    "type": t.transformation_type.value,
                    "description": t.description
                }
                for t in self.active_transformations
            ],
            "total_aetherfalls": len(self.aetherfall_history)
        }

    def get_aetherfall_history(self, limit: int = 10) -> List[AetherfallEvent]:
        """Get recent Aetherfall events."""
        return self.aetherfall_history[-limit:]

    def get_transformation_by_name(self, name: str) -> Optional[RealityTransformation]:
        """Get an active transformation by name."""
        for trans in self.active_transformations:
            if trans.name == name:
                return trans
        return None

    def should_trigger_aetherfall(self) -> bool:
        """Check if Aetherfall should be triggered automatically."""
        # Auto-trigger if stability hits 0
        return self.reality_stability <= 0

    def save_state_to_db(self):
        """Save reality state to database."""
        if not self.db_session:
            return

        try:
            from database.models import GameState

            # Save current cycle
            self._save_game_state("reality_cycle", self.current_cycle, "int")

            # Save reality state
            self._save_game_state("reality_state", self.reality_state.value, "string")

            # Save stability
            self._save_game_state("reality_stability", self.reality_stability, "float")

            # Save active transformations
            transformations_data = [
                {
                    "type": t.transformation_type.value,
                    "name": t.name,
                    "description": t.description,
                    "effects": t.effects,
                    "duration": t.duration,
                    "applied_at": t.applied_at.isoformat() if t.applied_at else None
                }
                for t in self.active_transformations
            ]
            self._save_game_state(
                "reality_transformations",
                json.dumps(transformations_data),
                "json"
            )

            # Save Aetherfall history
            history_data = [
                {
                    "cycle_number": e.cycle_number,
                    "triggered_at": e.triggered_at.isoformat(),
                    "winning_faction": e.winning_faction,
                    "reality_changes": e.reality_changes,
                    "survivors": e.survivors,
                    "transformations_applied": e.transformations_applied
                }
                for e in self.aetherfall_history
            ]
            self._save_game_state(
                "aetherfall_history",
                json.dumps(history_data),
                "json"
            )

            self.db_session.commit()

        except Exception as e:
            print(f"Error saving reality state to database: {e}")
            self.db_session.rollback()

    def load_state_from_db(self):
        """Load reality state from database."""
        if not self.db_session:
            return

        try:
            from database.models import GameState

            # Load current cycle
            cycle_state = self.db_session.query(GameState).filter_by(
                key="reality_cycle"
            ).first()
            if cycle_state:
                self.current_cycle = int(cycle_state.value)

            # Load reality state
            state_state = self.db_session.query(GameState).filter_by(
                key="reality_state"
            ).first()
            if state_state:
                self.reality_state = RealityState(state_state.value)

            # Load stability
            stability_state = self.db_session.query(GameState).filter_by(
                key="reality_stability"
            ).first()
            if stability_state:
                self.reality_stability = float(stability_state.value)

            # Load active transformations
            trans_state = self.db_session.query(GameState).filter_by(
                key="reality_transformations"
            ).first()
            if trans_state and trans_state.value_type == "json":
                trans_data = json.loads(trans_state.value)
                self.active_transformations = [
                    RealityTransformation(
                        transformation_type=TransformationType(t["type"]),
                        name=t["name"],
                        description=t["description"],
                        effects=t["effects"],
                        duration=t.get("duration"),
                        applied_at=datetime.fromisoformat(t["applied_at"]) if t.get("applied_at") else None
                    )
                    for t in trans_data
                ]

            # Load Aetherfall history
            history_state = self.db_session.query(GameState).filter_by(
                key="aetherfall_history"
            ).first()
            if history_state and history_state.value_type == "json":
                history_data = json.loads(history_state.value)
                self.aetherfall_history = [
                    AetherfallEvent(
                        cycle_number=e["cycle_number"],
                        triggered_at=datetime.fromisoformat(e["triggered_at"]),
                        winning_faction=e.get("winning_faction"),
                        reality_changes=e.get("reality_changes", {}),
                        survivors=e.get("survivors", []),
                        transformations_applied=e.get("transformations_applied", [])
                    )
                    for e in history_data
                ]

        except Exception as e:
            print(f"Error loading reality state from database: {e}")

    def _save_game_state(self, key: str, value: Any, value_type: str):
        """Helper to save a game state value."""
        from database.models import GameState

        state = self.db_session.query(GameState).filter_by(key=key).first()

        if state:
            state.value = str(value)
            state.value_type = value_type
        else:
            state = GameState(
                key=key,
                value=str(value),
                value_type=value_type
            )
            self.db_session.add(state)

    def clear_all_transformations(self):
        """Clear all active transformations (admin command)."""
        self.active_transformations = []
        self.reality_stability = 100.0
        self.reality_state = RealityState.STABLE

        if self.db_session:
            self.save_state_to_db()

    def simulate_aetherfall_countdown(self) -> Dict[str, Any]:
        """
        Simulate countdown to Aetherfall based on current conditions.
        Returns estimated time/events until Aetherfall triggers.
        """
        # This could calculate based on:
        # - Current stability degradation rate
        # - Faction progress toward 12 shards
        # - Active conflicts
        # - etc.

        from world.shards import ShardManager
        shard_manager = ShardManager(self.db_session)

        # Check if any faction is close to winning
        distribution = shard_manager.get_shard_distribution()
        max_shards = max(distribution.values()) if distribution else 0

        return {
            "stability": self.reality_stability,
            "state": self.reality_state.value,
            "max_faction_shards": max_shards,
            "shards_to_victory": 12 - max_shards,
            "estimated_stability_collapse": "unknown",  # Would need degradation rate
            "imminent": max_shards >= 10 or self.reality_stability < 20
        }

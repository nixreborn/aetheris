#!/usr/bin/env python3
"""
Shards of Eternity - Admin CLI Tool

Comprehensive command-line interface for server administration, world management,
player management, and system monitoring.

Usage:
    python -m admin.cli <command> [options]

Examples:
    python -m admin.cli start-server
    python -m admin.cli list-players
    python -m admin.cli trigger-aetherfall
    python -m admin.cli backup-db
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import subprocess
import signal

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.tree import Tree
from rich import box

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from database import get_db_session, init_database, reset_database
from database.models import (
    Character, CrystalShard, WorldState, WorldEvent, Party,
    RealityType, FactionType, ShardOwnership
)
from world.reality import RealityManager
from world.shards import ShardManager, ShardStatus

console = Console()
settings = get_settings()

# Server process tracking
server_process = None
server_pid_file = Path("./data/server.pid")

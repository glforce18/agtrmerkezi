"""
AGTR Merkezi - Config Management Service
Handles server.cfg parsing, CVAR editing, config templates, and backups
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.database import ConfigTemplate, GameServer

logger = logging.getLogger(__name__)


class ConfigService:
    """Service for managing server configurations"""

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # server.cfg Management
    # =========================

    def parse_server_cfg(self, server_path: Path) -> Dict[str, str]:
        """
        Parse server.cfg file into dict of CVARs

        Args:
            server_path: Path to server directory

        Returns:
            Dict of CVAR name -> value
        """
        cfg_path = server_path / "valve" / "server.cfg"
        cvars = {}

        try:
            if not cfg_path.exists():
                logger.warning(f"server.cfg not found: {cfg_path}")
                return cvars

            with open(cfg_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("//") or line.startswith("#"):
                        continue

                    # Match: cvar_name "value" or cvar_name value
                    match = re.match(r'(\w+)\s+"?([^"]*)"?', line)
                    if match:
                        cvar_name, cvar_value = match.groups()
                        cvars[cvar_name] = cvar_value.strip('"')

            logger.info(f"Parsed {len(cvars)} CVARs from server.cfg")
            return cvars

        except Exception as e:
            logger.error(f"Failed to parse server.cfg: {e}")
            return {}

    def update_server_cfg(
        self, server_path: Path, cvars: Dict[str, str], backup: bool = True
    ) -> bool:
        """
        Update server.cfg with new CVAR values

        Args:
            server_path: Path to server directory
            cvars: Dict of CVAR name -> value to update
            backup: Create backup before updating

        Returns:
            True if successful
        """
        cfg_path = server_path / "valve" / "server.cfg"

        try:
            # Create backup if requested
            if backup and cfg_path.exists():
                backup_path = cfg_path.with_suffix(".cfg.bak")
                import shutil

                shutil.copy2(cfg_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

            # Read existing config
            if cfg_path.exists():
                with open(cfg_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            else:
                lines = []

            # Update CVARs
            updated_lines = []
            updated_cvars = set()

            for line in lines:
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                    updated_lines.append(line)
                    continue

                # Check if this line contains a CVAR we want to update
                match = re.match(r'(\w+)\s+"?([^"]*)"?', stripped)
                if match:
                    cvar_name, _ = match.groups()
                    if cvar_name in cvars:
                        # Update this CVAR
                        updated_lines.append(f'{cvar_name} "{cvars[cvar_name]}"\n')
                        updated_cvars.add(cvar_name)
                    else:
                        # Keep original line
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            # Add new CVARs that weren't in the file
            for cvar_name, cvar_value in cvars.items():
                if cvar_name not in updated_cvars:
                    updated_lines.append(f'{cvar_name} "{cvar_value}"\n')

            # Write updated config
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.writelines(updated_lines)

            logger.info(f"Updated {len(cvars)} CVARs in server.cfg")
            return True

        except Exception as e:
            logger.error(f"Failed to update server.cfg: {e}")
            return False

    # =========================
    # Config Templates
    # =========================

    def get_templates(
        self, game_type: Optional[str] = None, user_id: Optional[int] = None
    ) -> List[ConfigTemplate]:
        """Get available config templates"""
        query = self.db.query(ConfigTemplate)

        if game_type:
            query = query.filter(ConfigTemplate.game_type == game_type)

        # Show public templates + user's own templates
        if user_id:
            query = query.filter(
                (ConfigTemplate.is_public == True)  # noqa: E712
                | (ConfigTemplate.owner_id == user_id)
            )
        else:
            query = query.filter(ConfigTemplate.is_public == True)  # noqa: E712

        return query.order_by(ConfigTemplate.is_official.desc(), ConfigTemplate.name).all()

    def create_template(
        self,
        name: str,
        game_type: str,
        preset_type: str,
        config_content: str,
        owner_id: int,
        **kwargs,
    ) -> ConfigTemplate:
        """Create a new config template"""
        template = ConfigTemplate(
            name=name,
            game_type=game_type,
            preset_type=preset_type,
            config_content=config_content,
            owner_id=owner_id,
            **kwargs,
        )
        self.db.add(template)
        self.db.commit()
        logger.info(f"Created config template: {name}")
        return template

    def apply_template(self, server_id: int, template_id: int) -> bool:
        """Apply a config template to a server"""
        template = self.db.query(ConfigTemplate).filter_by(id=template_id).first()
        if not template:
            logger.error(f"Template {template_id} not found")
            return False

        server = self.db.query(GameServer).filter_by(id=server_id).first()
        if not server:
            logger.error(f"Server {server_id} not found")
            return False

        # Get server path
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        # Write template content to server.cfg
        cfg_path = server_path / "valve" / "server.cfg"
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(template.config_content)

            # Increment use count
            template.use_count += 1
            self.db.commit()

            logger.info(f"Applied template {template.name} to server {server_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply template: {e}")
            return False

    # =========================
    # MOTD Management
    # =========================

    def get_motd(self, server_path: Path) -> str:
        """Get MOTD HTML content"""
        motd_path = server_path / "valve" / "motd.txt"

        try:
            if motd_path.exists():
                with open(motd_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception as e:
            logger.error(f"Failed to read MOTD: {e}")
            return ""

    def update_motd(self, server_path: Path, html_content: str) -> bool:
        """Update MOTD HTML content"""
        motd_path = server_path / "valve" / "motd.txt"

        try:
            # Sanitize HTML (basic XSS prevention)
            # TODO: Use bleach library for proper sanitization
            sanitized_html = html_content

            with open(motd_path, "w", encoding="utf-8") as f:
                f.write(sanitized_html)

            logger.info("Updated MOTD")
            return True

        except Exception as e:
            logger.error(f"Failed to update MOTD: {e}")
            return False

    # =========================
    # Mapcycle Management
    # =========================

    def get_mapcycle(self, server_path: Path) -> List[str]:
        """Get list of maps from mapcycle.txt"""
        mapcycle_path = server_path / "valve" / "mapcycle.txt"

        try:
            if not mapcycle_path.exists():
                return []

            with open(mapcycle_path, "r", encoding="utf-8") as f:
                maps = [line.strip() for line in f if line.strip()]

            return maps

        except Exception as e:
            logger.error(f"Failed to read mapcycle: {e}")
            return []

    def update_mapcycle(self, server_path: Path, maps: List[str]) -> bool:
        """Update mapcycle.txt with new map list"""
        mapcycle_path = server_path / "valve" / "mapcycle.txt"

        try:
            with open(mapcycle_path, "w", encoding="utf-8") as f:
                for map_name in maps:
                    f.write(f"{map_name}\n")

            logger.info(f"Updated mapcycle with {len(maps)} maps")
            return True

        except Exception as e:
            logger.error(f"Failed to update mapcycle: {e}")
            return False

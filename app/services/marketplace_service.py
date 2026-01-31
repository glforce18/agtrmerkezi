"""
AGTR Merkezi - Plugin Marketplace Service
Handles community plugin store, plugin discovery, and installation
"""

import hashlib
import logging
from pathlib import Path
from typing import List, Optional

import requests
from sqlalchemy.orm import Session

from app.models.database import PluginMarketplace

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Service for plugin marketplace"""

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # Marketplace Browsing
    # =========================

    def get_plugins(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PluginMarketplace]:
        """Browse marketplace plugins"""
        query = self.db.query(PluginMarketplace).filter_by(is_active=True)

        if category:
            query = query.filter_by(category=category)

        if search:
            query = query.filter(
                (PluginMarketplace.name.contains(search))
                | (PluginMarketplace.description.contains(search))
            )

        if verified_only:
            query = query.filter_by(is_verified=True)

        # Order by rating and install count
        query = query.order_by(
            PluginMarketplace.is_verified.desc(),
            PluginMarketplace.rating.desc(),
            PluginMarketplace.install_count.desc(),
        )

        return query.limit(limit).offset(offset).all()

    def get_plugin(self, plugin_id: int) -> Optional[PluginMarketplace]:
        """Get a specific plugin by ID"""
        return self.db.query(PluginMarketplace).filter_by(id=plugin_id).first()

    def get_categories(self) -> List[str]:
        """Get all plugin categories"""
        categories = (
            self.db.query(PluginMarketplace.category).filter_by(is_active=True).distinct().all()
        )
        return [c[0] for c in categories]

    # =========================
    # Plugin Installation
    # =========================

    def install_plugin(self, server_id: int, plugin_id: int) -> dict:
        """
        Install a plugin from marketplace to a server

        Returns:
            Dict with success, message, plugin_filename
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return {"success": False, "message": "Plugin not found"}

        # Download plugin file
        try:
            response = requests.get(plugin.file_url, timeout=30)
            response.raise_for_status()
            plugin_data = response.content

            # Verify file hash if available
            if plugin.file_hash:
                downloaded_hash = hashlib.sha256(plugin_data).hexdigest()
                if downloaded_hash != plugin.file_hash:
                    return {
                        "success": False,
                        "message": "File hash mismatch - possible corruption or security issue",
                    }

            # Install to server
            server_path = Path(f"/home/gameservers/servers/server_{server_id}")
            plugins_path = server_path / "valve" / "addons" / "amxmodx" / "plugins"

            # Ensure plugins directory exists
            plugins_path.mkdir(parents=True, exist_ok=True)

            # Write plugin file
            plugin_file = plugins_path / plugin.filename
            with open(plugin_file, "wb") as f:
                f.write(plugin_data)

            # Increment install count
            plugin.install_count += 1
            self.db.commit()

            logger.info(f"Installed plugin {plugin.name} to server {server_id}")
            return {
                "success": True,
                "message": f"Plugin {plugin.name} installed successfully",
                "plugin_filename": plugin.filename,
            }

        except requests.RequestException as e:
            logger.error(f"Failed to download plugin: {e}")
            return {"success": False, "message": f"Download failed: {e}"}
        except Exception as e:
            logger.error(f"Failed to install plugin: {e}")
            return {"success": False, "message": f"Installation failed: {e}"}

    # =========================
    # Plugin Submission & Management
    # =========================

    def submit_plugin(
        self,
        name: str,
        filename: str,
        category: str,
        file_url: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> PluginMarketplace:
        """
        Submit a new plugin to marketplace

        Note: Plugins start as is_verified=False and need admin approval
        """
        plugin = PluginMarketplace(
            name=name,
            filename=filename,
            category=category,
            file_url=file_url,
            description=description,
            is_verified=False,  # Requires admin approval
            **kwargs,
        )
        self.db.add(plugin)
        self.db.commit()

        logger.info(f"Submitted plugin {name} to marketplace (pending verification)")
        return plugin

    def update_plugin(self, plugin_id: int, **updates) -> Optional[PluginMarketplace]:
        """Update plugin metadata"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return None

        for key, value in updates.items():
            if hasattr(plugin, key):
                setattr(plugin, key, value)

        self.db.commit()
        return plugin

    def verify_plugin(self, plugin_id: int, verified: bool = True) -> bool:
        """Verify/unverify a plugin (admin only)"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False

        plugin.is_verified = verified
        self.db.commit()

        logger.info(f"Plugin {plugin.name} verification set to {verified}")
        return True

    def delete_plugin(self, plugin_id: int) -> bool:
        """Soft delete a plugin (set is_active=False)"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False

        plugin.is_active = False
        self.db.commit()

        logger.info(f"Deleted plugin {plugin.name} from marketplace")
        return True

    # =========================
    # Ratings & Reviews
    # =========================

    def rate_plugin(self, plugin_id: int, rating: float) -> bool:
        """
        Add a rating to a plugin (1-5 stars)

        Note: Full review system would need a separate PluginReview model
        """
        if not 1 <= rating <= 5:
            return False

        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False

        # Update average rating (simple moving average)
        current_total = plugin.rating * plugin.rating_count
        new_total = current_total + rating
        plugin.rating_count += 1
        plugin.rating = round(new_total / plugin.rating_count, 2)

        self.db.commit()
        return True

    # =========================
    # Statistics
    # =========================

    def get_popular_plugins(self, limit: int = 10) -> List[PluginMarketplace]:
        """Get most installed plugins"""
        return (
            self.db.query(PluginMarketplace)
            .filter_by(is_active=True)
            .order_by(PluginMarketplace.install_count.desc())
            .limit(limit)
            .all()
        )

    def get_top_rated_plugins(self, limit: int = 10) -> List[PluginMarketplace]:
        """Get highest rated plugins"""
        return (
            self.db.query(PluginMarketplace)
            .filter_by(is_active=True)
            .filter(PluginMarketplace.rating_count >= 5)  # At least 5 ratings
            .order_by(PluginMarketplace.rating.desc())
            .limit(limit)
            .all()
        )

"""
AGTR Merkezi - Role Management API
Discord-like role system with permissions
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.connection import get_db
from app.models.database import (
    User, Role, UserRoleAssignment, DEFAULT_PERMISSIONS
)
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== SCHEMAS ====================

class RoleCreate(BaseModel):
    name: str
    display_name: str
    color: str = "#ffffff"
    icon: Optional[str] = None
    priority: int = 0
    permissions: dict = {}


class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    priority: Optional[int] = None
    permissions: Optional[dict] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    color: str
    icon: Optional[str]
    priority: int
    permissions: dict
    is_default: bool
    is_system: bool
    user_count: int = 0

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    role_id: int
    user_id: Optional[int] = None
    steam_id: Optional[str] = None
    username_pattern: Optional[str] = None
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None


class UserRolesResponse(BaseModel):
    user_id: int
    username: str
    steam_id: Optional[str]
    roles: List[RoleResponse]


# ==================== HELPER FUNCTIONS ====================

def check_permission(user: User, permission: str, db: Session) -> bool:
    """Check if user has a specific permission"""
    # Superadmin has all permissions
    if user.role and user.role.value == "superadmin":
        return True

    # Check role assignments
    assignments = db.query(UserRoleAssignment).filter(
        (UserRoleAssignment.user_id == user.id) |
        (UserRoleAssignment.steam_id == user.steam_id)
    ).all()

    for assignment in assignments:
        # Check expiration
        if assignment.expires_at and assignment.expires_at < datetime.utcnow():
            continue

        role = assignment.role
        if role.permissions and role.permissions.get(permission):
            return True

    return False


def get_user_roles(user: User, db: Session) -> List[Role]:
    """Get all roles for a user"""
    roles = []

    # Get by user_id
    assignments = db.query(UserRoleAssignment).filter(
        UserRoleAssignment.user_id == user.id
    ).all()

    # Get by steam_id
    if user.steam_id:
        steam_assignments = db.query(UserRoleAssignment).filter(
            UserRoleAssignment.steam_id == user.steam_id
        ).all()
        assignments.extend(steam_assignments)

    # Get by username pattern (simple LIKE matching)
    pattern_assignments = db.query(UserRoleAssignment).filter(
        UserRoleAssignment.username_pattern.isnot(None)
    ).all()

    for pa in pattern_assignments:
        pattern = pa.username_pattern.replace("*", "%")
        if user.username and db.query(User).filter(
            User.id == user.id,
            User.username.like(pattern)
        ).first():
            assignments.append(pa)

    # Extract unique roles, check expiration
    seen_role_ids = set()
    for assignment in assignments:
        if assignment.expires_at and assignment.expires_at < datetime.utcnow():
            continue
        if assignment.role_id not in seen_role_ids:
            roles.append(assignment.role)
            seen_role_ids.add(assignment.role_id)

    # Sort by priority (highest first)
    roles.sort(key=lambda r: r.priority, reverse=True)
    return roles


def get_user_permissions(user: User, db: Session) -> dict:
    """Get merged permissions for a user"""
    permissions = DEFAULT_PERMISSIONS.copy()

    # Superadmin gets everything
    if user.role and user.role.value == "superadmin":
        return {k: True for k in permissions.keys()}

    # Legacy admin check
    if user.role and user.role.value == "admin":
        permissions["admin.access"] = True
        permissions["admin.users.view"] = True
        permissions["admin.servers.view"] = True

    # Merge permissions from roles
    roles = get_user_roles(user, db)
    for role in roles:
        if role.permissions:
            for key, value in role.permissions.items():
                if value:  # Only grant, never revoke via merge
                    permissions[key] = True

    return permissions


def require_permission(permission: str):
    """Dependency to require a specific permission"""
    def check(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not check_permission(current_user, permission, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    return check


# ==================== ROLE CRUD ====================

@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all roles"""
    roles = db.query(Role).order_by(Role.priority.desc()).all()

    result = []
    for role in roles:
        user_count = db.query(UserRoleAssignment).filter(
            UserRoleAssignment.role_id == role.id
        ).count()

        result.append(RoleResponse(
            id=role.id,
            name=role.name,
            display_name=role.display_name,
            color=role.color,
            icon=role.icon,
            priority=role.priority,
            permissions=role.permissions or {},
            is_default=role.is_default,
            is_system=role.is_system,
            user_count=user_count
        ))

    return result


@router.post("/", response_model=RoleResponse)
async def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin.roles.manage"))
):
    """Create a new role"""
    # Check if name exists
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu isimde bir rol zaten var")

    # Merge with default permissions
    permissions = DEFAULT_PERMISSIONS.copy()
    permissions.update(data.permissions)

    role = Role(
        name=data.name,
        display_name=data.display_name,
        color=data.color,
        icon=data.icon,
        priority=data.priority,
        permissions=permissions
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    logger.info(f"Role created: {role.name} by user {current_user.id}")

    return RoleResponse(
        id=role.id,
        name=role.name,
        display_name=role.display_name,
        color=role.color,
        icon=role.icon,
        priority=role.priority,
        permissions=role.permissions,
        is_default=role.is_default,
        is_system=role.is_system,
        user_count=0
    )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin.roles.manage"))
):
    """Update a role"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol bulunamadı")

    if data.display_name is not None:
        role.display_name = data.display_name
    if data.color is not None:
        role.color = data.color
    if data.icon is not None:
        role.icon = data.icon
    if data.priority is not None:
        role.priority = data.priority
    if data.permissions is not None:
        # Merge with existing
        current_perms = role.permissions or {}
        current_perms.update(data.permissions)
        role.permissions = current_perms

    db.commit()
    db.refresh(role)

    user_count = db.query(UserRoleAssignment).filter(
        UserRoleAssignment.role_id == role.id
    ).count()

    return RoleResponse(
        id=role.id,
        name=role.name,
        display_name=role.display_name,
        color=role.color,
        icon=role.icon,
        priority=role.priority,
        permissions=role.permissions,
        is_default=role.is_default,
        is_system=role.is_system,
        user_count=user_count
    )


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin.roles.manage"))
):
    """Delete a role"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol bulunamadı")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Sistem rolleri silinemez")

    db.delete(role)
    db.commit()

    logger.info(f"Role deleted: {role.name} by user {current_user.id}")

    return {"message": "Rol silindi"}


# ==================== ROLE ASSIGNMENTS ====================

@router.post("/assign")
async def assign_role(
    data: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin.roles.manage"))
):
    """Assign a role to user(s)"""
    # Validate role exists
    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol bulunamadı")

    # Need at least one target
    if not data.user_id and not data.steam_id and not data.username_pattern:
        raise HTTPException(status_code=400, detail="user_id, steam_id veya username_pattern gerekli")

    # Check for existing assignment
    query = db.query(UserRoleAssignment).filter(
        UserRoleAssignment.role_id == data.role_id
    )

    if data.user_id:
        existing = query.filter(UserRoleAssignment.user_id == data.user_id).first()
    elif data.steam_id:
        existing = query.filter(UserRoleAssignment.steam_id == data.steam_id).first()
    elif data.username_pattern:
        existing = query.filter(UserRoleAssignment.username_pattern == data.username_pattern).first()
    else:
        existing = None

    if existing:
        raise HTTPException(status_code=400, detail="Bu rol zaten atanmış")

    assignment = UserRoleAssignment(
        role_id=data.role_id,
        user_id=data.user_id,
        steam_id=data.steam_id,
        username_pattern=data.username_pattern,
        assigned_by=current_user.id,
        reason=data.reason,
        expires_at=data.expires_at
    )

    db.add(assignment)
    db.commit()

    target = data.user_id or data.steam_id or data.username_pattern
    logger.info(f"Role {role.name} assigned to {target} by user {current_user.id}")

    return {"message": "Rol atandı", "assignment_id": assignment.id}


@router.delete("/assign/{assignment_id}")
async def remove_role_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin.roles.manage"))
):
    """Remove a role assignment"""
    assignment = db.query(UserRoleAssignment).filter(
        UserRoleAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Rol ataması bulunamadı")

    db.delete(assignment)
    db.commit()

    return {"message": "Rol ataması kaldırıldı"}


@router.get("/user/{user_id}", response_model=UserRolesResponse)
async def get_user_roles_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get roles for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    roles = get_user_roles(user, db)

    return UserRolesResponse(
        user_id=user.id,
        username=user.username,
        steam_id=user.steam_id,
        roles=[
            RoleResponse(
                id=r.id,
                name=r.name,
                display_name=r.display_name,
                color=r.color,
                icon=r.icon,
                priority=r.priority,
                permissions=r.permissions or {},
                is_default=r.is_default,
                is_system=r.is_system
            ) for r in roles
        ]
    )


@router.get("/my-roles")
async def get_my_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's roles and permissions"""
    roles = get_user_roles(current_user, db)
    permissions = get_user_permissions(current_user, db)

    return {
        "roles": [
            {
                "id": r.id,
                "name": r.name,
                "display_name": r.display_name,
                "color": r.color,
                "icon": r.icon
            } for r in roles
        ],
        "permissions": permissions,
        "is_admin": permissions.get("admin.access", False)
    }


@router.get("/permissions")
async def list_permissions(
    current_user: User = Depends(get_current_user)
):
    """List all available permissions"""
    # Group permissions by category
    categories = {}

    for perm in DEFAULT_PERMISSIONS.keys():
        parts = perm.split(".")
        category = parts[0] if len(parts) > 1 else "general"

        if category not in categories:
            categories[category] = []
        categories[category].append(perm)

    return {
        "permissions": DEFAULT_PERMISSIONS,
        "categories": categories
    }


# ==================== INITIALIZATION ====================

def initialize_default_roles(db: Session):
    """Create default roles if they don't exist"""
    default_roles = [
        {
            "name": "member",
            "display_name": "Üye",
            "color": "#94a3b8",
            "priority": 0,
            "is_default": True,
            "is_system": True,
            "permissions": {
                "forum.post": True,
                "forum.edit_own": True,
                "shop.purchase": True,
                "jackpot.play": True
            }
        },
        {
            "name": "vip",
            "display_name": "VIP",
            "color": "#fbbf24",
            "icon": "⭐",
            "priority": 10,
            "permissions": {
                "forum.post": True,
                "forum.edit_own": True,
                "shop.purchase": True,
                "shop.discount": True,
                "jackpot.play": True,
                "jackpot.high_limit": True,
                "servers.create": True
            }
        },
        {
            "name": "admin",
            "display_name": "Admin",
            "color": "#3b82f6",
            "icon": "🛡️",
            "priority": 80,
            "is_system": True,
            "permissions": {
                "admin.access": True,
                "admin.users.view": True,
                "admin.users.edit": True,
                "admin.users.ban": True,
                "admin.servers.view": True,
                "admin.servers.edit": True,
                "forum.moderate": True,
                "forum.pin": True,
                "forum.lock": True,
                "forum.edit_any": True,
                "forum.delete_any": True,
                "servers.manage_any": True
            }
        },
        {
            "name": "bas_admin",
            "display_name": "Baş Admin",
            "color": "#8b5cf6",
            "icon": "👑",
            "priority": 90,
            "permissions": {
                "admin.access": True,
                "admin.users.view": True,
                "admin.users.edit": True,
                "admin.users.ban": True,
                "admin.users.delete": True,
                "admin.roles.manage": True,
                "admin.servers.view": True,
                "admin.servers.edit": True,
                "admin.servers.delete": True,
                "admin.payments.view": True,
                "admin.payments.manage": True,
                "admin.settings.view": True,
                "admin.settings.edit": True,
                "admin.announcements.manage": True,
                "forum.moderate": True,
                "forum.pin": True,
                "forum.lock": True,
                "forum.edit_any": True,
                "forum.delete_any": True,
                "servers.manage_any": True,
                "bypass_cooldowns": True,
                "see_hidden": True
            }
        },
        {
            "name": "sunucu_sahibi",
            "display_name": "Sunucu Sahibi",
            "color": "#ef4444",
            "icon": "🔥",
            "priority": 100,
            "is_system": True,
            "permissions": {k: True for k in DEFAULT_PERMISSIONS.keys()}  # All permissions
        }
    ]

    for role_data in default_roles:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            logger.info(f"Created default role: {role_data['name']}")

    db.commit()

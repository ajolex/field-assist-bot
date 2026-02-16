"""Role-based access helpers."""

import discord


SRA_ROLE = "SRA"
FC_ROLE = "FC"
FO_ROLE = "FO"


def can_request_reopen(role: str) -> bool:
	"""Return whether a role can request case reopening."""

	return role in {SRA_ROLE, FC_ROLE}


def is_admin(role: str) -> bool:
	"""Return whether a role is administrative."""

	return role == SRA_ROLE


def member_roles(member: discord.Member | None) -> set[str]:
	"""Extract role names from discord member."""

	if member is None:
		return set()
	return {role.name for role in member.roles}


def has_any_role(member: discord.Member | None, allowed_roles: set[str]) -> bool:
	"""Check if member has at least one of the allowed roles."""

	return bool(member_roles(member) & allowed_roles)

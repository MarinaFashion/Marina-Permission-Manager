from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import frappe
from frappe import _
from frappe.utils import cint, cstr

MAX_BATCH_USERS = 500
STANDARD_USERS = ("Administrator", "Guest")


def _only_system_manager() -> None:
	frappe.only_for("System Manager")


def _validate_rule(
	allow: str,
	for_value: str,
	apply_to_all_doctypes: int | str | bool,
	applicable_for: str | None,
) -> tuple[bool, str]:
	if not allow or not frappe.db.exists("DocType", {"name": allow, "istable": 0}):
		frappe.throw(_("Please select a valid non-child Document Type in Allow."))
	if not for_value or not frappe.db.exists(allow, for_value):
		frappe.throw(_("Please select a valid {0} in For Value.").format(frappe.bold(allow)))

	apply_to_all = bool(cint(apply_to_all_doctypes))
	applicable = cstr(applicable_for).strip()
	if apply_to_all:
		applicable = ""
	elif not applicable:
		frappe.throw(_("Applicable For is required when Apply To All Document Types is disabled."))
	elif not frappe.db.exists("DocType", {"name": applicable, "istable": 0}):
		frappe.throw(_("Please select a valid non-child Document Type in Applicable For."))

	return apply_to_all, applicable


def _rule_filters(
	allow: str,
	for_value: str,
	apply_to_all: bool,
	applicable_for: str,
) -> dict[str, Any]:
	return {
		"allow": allow,
		"for_value": for_value,
		"apply_to_all_doctypes": int(apply_to_all),
		"applicable_for": applicable_for,
	}


def _desk_users() -> list[Any]:
	return frappe.get_all(
		"User",
		filters={
			"user_type": "System User",
			"name": ("not in", STANDARD_USERS),
		},
		fields=["name", "full_name", "enabled"],
		order_by="enabled desc, full_name asc, name asc",
	)


@frappe.whitelist()
def get_user_permission_users(
	allow: str,
	for_value: str,
	apply_to_all_doctypes: int | str | bool = 1,
	applicable_for: str | None = None,
) -> dict[str, Any]:
	"""Return Desk users and their exact match for one User Permission rule."""
	_only_system_manager()
	apply_to_all, applicable = _validate_rule(
		allow, for_value, apply_to_all_doctypes, applicable_for
	)
	users = _desk_users()
	user_names = [user.name for user in users]

	matching: dict[str, Any] = {}
	permission_counts: Counter[str] = Counter()
	default_permissions: dict[str, list[Any]] = defaultdict(list)
	if user_names:
		for row in frappe.get_all(
			"User Permission",
			filters={"user": ("in", user_names), "allow": allow},
			fields=[
				"name",
				"user",
				"for_value",
				"applicable_for",
				"apply_to_all_doctypes",
				"is_default",
			],
		):
			permission_counts[row.user] += 1
			if row.is_default:
				default_permissions[row.user].append(row)
			if (
				row.for_value == for_value
				and bool(row.apply_to_all_doctypes) == apply_to_all
				and cstr(row.applicable_for) == applicable
			):
				matching[row.user] = row

	return {
		"rule": {
			"allow": allow,
			"for_value": for_value,
			"apply_to_all_doctypes": apply_to_all,
			"applicable_for": applicable,
		},
		"users": [
			{
				"user": user.name,
				"full_name": user.full_name or user.name,
				"enabled": bool(user.enabled),
				"assigned": user.name in matching,
				"permission": matching[user.name].name if user.name in matching else None,
				"is_default": bool(matching[user.name].is_default) if user.name in matching else False,
				"other_permissions": permission_counts[user.name] - int(user.name in matching),
				"other_default": next(
					(
						row.for_value
						for row in default_permissions[user.name]
						if (user.name not in matching or row.name != matching[user.name].name)
						and (cstr(row.applicable_for) == applicable or bool(row.apply_to_all_doctypes))
					),
					None,
				),
			}
			for user in users
		],
	}


def _default_conflicts(
	users: list[str],
	allow: str,
	applicable_for: str,
	exact_permissions: dict[str, Any],
) -> list[str]:
	conflicts = []
	for user in users:
		exact_name = exact_permissions[user].name if user in exact_permissions else ""
		filters: dict[str, Any] = {
			"user": user,
			"allow": allow,
			"is_default": 1,
		}
		if exact_name:
			filters["name"] = ("!=", exact_name)
		if frappe.get_all(
			"User Permission",
			filters=filters,
			or_filters={
				"applicable_for": applicable_for,
				"apply_to_all_doctypes": 1,
			},
			limit=1,
		):
			conflicts.append(user)
	return conflicts


@frappe.whitelist()
def save_user_permission_users(
	allow: str,
	for_value: str,
	apply_to_all_doctypes: int | str | bool,
	applicable_for: str | None,
	is_default: int | str | bool,
	changes: str | list[dict[str, Any]],
) -> dict[str, int]:
	"""Bulk add, update, or remove one exact User Permission rule across users."""
	_only_system_manager()
	apply_to_all, applicable = _validate_rule(
		allow, for_value, apply_to_all_doctypes, applicable_for
	)
	default = bool(cint(is_default))
	parsed_changes = frappe.parse_json(changes) if isinstance(changes, str) else changes
	if not isinstance(parsed_changes, list):
		frappe.throw(_("User Permission changes must be a list."))
	if len(parsed_changes) > MAX_BATCH_USERS:
		frappe.throw(_("A maximum of {0} users can be changed in one save.").format(MAX_BATCH_USERS))
	if any(not isinstance(change, dict) or not change.get("user") for change in parsed_changes):
		frappe.throw(_("Every User Permission change must include a user."))

	requested_users = [change["user"] for change in parsed_changes]
	if len(requested_users) != len(set(requested_users)):
		frappe.throw(_("Each user can appear only once in the change list."))
	if set(requested_users).intersection(STANDARD_USERS):
		frappe.throw(_("Administrator and Guest cannot be managed here."))

	valid_users = {
		row.name: bool(row.enabled)
		for row in frappe.get_all(
			"User",
			filters={
				"user_type": "System User",
				"name": ("in", requested_users or [""]),
			},
			fields=["name", "enabled"],
		)
	}
	if set(valid_users) != set(requested_users):
		frappe.throw(_("One or more selected users cannot be managed here."))
	rule_filters = _rule_filters(allow, for_value, apply_to_all, applicable)
	exact_permissions = {
		row.user: row
		for row in frappe.get_all(
			"User Permission",
			filters={**rule_filters, "user": ("in", requested_users or [""])},
			fields=["name", "user", "is_default"],
		)
	}
	if any(
		bool(cint(change.get("assigned")))
		and not valid_users[change["user"]]
		and change["user"] not in exact_permissions
		for change in parsed_changes
	):
		frappe.throw(_("New User Permissions cannot be assigned to inactive users."))

	users_becoming_default = [
		change["user"]
		for change in parsed_changes
		if default and bool(cint(change.get("assigned")))
	]
	conflicts = _default_conflicts(users_becoming_default, allow, applicable, exact_permissions)
	if conflicts:
		preview = ", ".join(conflicts[:5])
		if len(conflicts) > 5:
			preview += _(" and {0} more").format(len(conflicts) - 5)
		frappe.throw(
			_("A different default {0} User Permission already exists for: {1}.").format(
				frappe.bold(allow), preview
			)
		)

	created = updated = deleted = 0
	for change in parsed_changes:
		user = change["user"]
		assigned = bool(cint(change.get("assigned")))
		existing = exact_permissions.get(user)
		if assigned and not existing:
			frappe.get_doc(
				{
					"doctype": "User Permission",
					"user": user,
					**rule_filters,
					"is_default": int(default),
				}
			).insert(ignore_permissions=True)
			created += 1
		elif assigned and existing and bool(existing.is_default) != default:
			doc = frappe.get_doc("User Permission", existing.name)
			doc.is_default = int(default)
			doc.save(ignore_permissions=True)
			updated += 1
		elif not assigned and existing:
			frappe.delete_doc("User Permission", existing.name, ignore_permissions=True)
			deleted += 1

	return {"created": created, "updated": updated, "deleted": deleted}

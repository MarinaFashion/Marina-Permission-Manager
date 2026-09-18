from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from marina_permission_manager.api.user_permissions import (
	_rule_filters,
	save_user_permission_users,
)


class TestBulkUserPermissions(TestCase):
	def test_rule_filters_preserve_exact_scope(self):
		self.assertEqual(
			_rule_filters("Warehouse", "Stores - MA", False, "Stock Entry"),
			{
				"allow": "Warehouse",
				"for_value": "Stores - MA",
				"apply_to_all_doctypes": 0,
				"applicable_for": "Stock Entry",
			},
		)

	@patch("marina_permission_manager.api.user_permissions._only_system_manager")
	@patch(
		"marina_permission_manager.api.user_permissions._validate_rule",
		return_value=(True, ""),
	)
	@patch.object(frappe, "delete_doc")
	@patch.object(frappe, "get_all")
	def test_existing_permission_can_be_removed_from_inactive_user(
		self,
		get_all,
		delete_doc,
		_validate_rule,
		_only_system_manager,
	):
		def rows(doctype, **kwargs):
			if doctype == "User":
				return [SimpleNamespace(name="inactive@example.com", enabled=0)]
			if doctype == "User Permission":
				return [
					SimpleNamespace(
						name="UP-0001",
						user="inactive@example.com",
						is_default=0,
					)
				]
			return []

		get_all.side_effect = rows
		result = save_user_permission_users(
			allow="Warehouse",
			for_value="Stores - MA",
			apply_to_all_doctypes=1,
			applicable_for=None,
			is_default=0,
			changes=[{"user": "inactive@example.com", "assigned": 0}],
		)

		self.assertEqual(result, {"created": 0, "updated": 0, "deleted": 1})
		delete_doc.assert_called_once_with(
			"User Permission", "UP-0001", ignore_permissions=True
		)

	@patch("marina_permission_manager.api.user_permissions._only_system_manager")
	@patch(
		"marina_permission_manager.api.user_permissions._validate_rule",
		return_value=(True, ""),
	)
	@patch.object(frappe, "get_all")
	def test_new_permission_is_blocked_for_inactive_user(
		self,
		get_all,
		_validate_rule,
		_only_system_manager,
	):
		get_all.side_effect = lambda doctype, **kwargs: (
			[SimpleNamespace(name="inactive@example.com", enabled=0)]
			if doctype == "User"
			else []
		)

		with self.assertRaises(frappe.ValidationError):
			save_user_permission_users(
				allow="Warehouse",
				for_value="Stores - MA",
				apply_to_all_doctypes=1,
				applicable_for=None,
				is_default=0,
				changes=[{"user": "inactive@example.com", "assigned": 1}],
			)

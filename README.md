# Permission Manager

An editable, module-grouped role-permission matrix for Frappe Framework and ERPNext v15.

Permission Manager lets a System Manager select one role and manage its DocType permissions in a single screen. DocTypes are grouped by installed application and module, with filters and module-level bulk actions.

## Compatibility

- Frappe Framework 15
- ERPNext 15 (optional; the app works with any Frappe v15 site)

## Installation

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/MarinaFashion/Marina-Permission-Manager.git --branch main
bench --site your-site install-app marina_permission_manager
bench --site your-site migrate
bench build --app marina_permission_manager
```

Open:

```text
/app/marina-permission-manager
```

Only users with the **System Manager** role can open the page or call its server methods.

## Current scope

- All non-child DocTypes, grouped by application and module
- Role-level permissions for Select, Read, Write, Create, Delete, Submit, Cancel, Amend, Report, Import, Export, Print, Email, and Share
- Existing permission levels and "If Owner" rules are displayed and editable
- New unconfigured DocTypes receive a Level 0, non-owner rule when permissions are selected
- Module-level bulk selection
- Application, module, status, and text filters
- Pending-change review before a single batch save
- Uses Frappe's `Custom DocPerm` mechanism and permission validation

Advanced-rule creation, Role Profiles, User Permissions, Pages, Reports, and Workspaces are intentionally outside the first prototype.

## License

MIT

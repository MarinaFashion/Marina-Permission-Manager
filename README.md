# Permission Manager

Bulk access-management tools and reporting for Frappe Framework and ERPNext v15.

Permission Manager lets a System Manager manage DocType role permissions, user module availability, User Permissions, Workspace roles, and Page/Report access from bulk-management screens. It also provides an access workspace, summary cards, and module-access reports.

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
/app/permission-manager-dashboard
/app/marina-permission-manager
/app/marina-user-module-manager
/app/marina-page-report-permission-manager
/app/marina-workspace-access-manager
/app/marina-user-permission-manager
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
- Select one installed module and manage its availability across all enabled Desk users
- Bulk availability selection with user, status, and Module Profile filters
- Profile-controlled users become individually managed only when their module access is changed
- Bulk role access management for Pages and Reports using Frappe's `Custom Role` mechanism
- Bulk allowed-role management for public Workspaces, with an active-user access preview
- Private Workspace owners and Page-based role overrides are shown without overwriting their native access rules
- Bulk User Permission assignment for one exact permitted document and scope across Desk users
- Active/inactive user filtering, with safe cleanup of permissions belonging to inactive users
- Permission Manager workspace with active-user, module, and workspace cards
- Users Available per Module and User Module Access Summary reports

Complex multi-rule editing remains available through Frappe's standard User Permission list.

## Releases

- **0.3.0** — Add bulk Workspace role management, inherited-user access preview, bulk User Permission management with active/inactive cleanup, responsive table sizing, and direct Page/Report links.
- **0.2.0** — Add the Permission Manager workspace, summary cards, module-access reports, bulk user-module management, bulk Page/Report role management, and clickable DocType links.
- **0.1.1** — Fix the Save Changes button on Frappe v15.
- **0.1.0** — Initial module-grouped permission matrix.

## License

MIT

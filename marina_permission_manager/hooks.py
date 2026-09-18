app_name = "marina_permission_manager"
app_title = "Permission Manager"
app_publisher = "Marina Fashion"
app_description = "Bulk role, module, Workspace, User Permission, Page, and Report access management for Frappe and ERPNext v15"
app_email = "a.hasan@marinafashion.com.sa"
app_license = "MIT"

required_apps = ["frappe"]

add_to_apps_screen = [
	{
		"name": "marina_permission_manager",
		"logo": "/assets/marina_permission_manager/images/permission-manager.svg",
		"title": "Permission Manager",
		"route": "/app/permission-manager-dashboard",
		"has_permission": "marina_permission_manager.api.permissions.has_app_permission",
	}
]

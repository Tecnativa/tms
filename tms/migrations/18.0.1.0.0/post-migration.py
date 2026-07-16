def migrate(env, version):
    """
    Migrate Open Route Service API Key from ir.config_parameter to res.company
    """
    old_key = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("base_geolocalize.openrouteservice_api_key")
    )
    if old_key:
        companies = env["res.company"].with_context(active_test=False).search([])
        companies.write({"openrouteservice_api_key": old_key})
        param = env["ir.config_parameter"].search(
            [("key", "=", "base_geolocalize.openrouteservice_api_key")]
        )
        if param:
            param.unlink()

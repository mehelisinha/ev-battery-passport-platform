"""Service layer: thin clients to each backing store.

Routers depend on these (not on raw drivers), so connection handling and query
logic live in one place per store (DRY). Credentials come from
common.config.Settings — never hardcoded.
"""

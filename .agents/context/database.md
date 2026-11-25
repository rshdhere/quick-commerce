# Persistence boundaries

This checkout currently has no application schema, migrations or selected database driver. When introducing persistence, record the engine, schema owner, migration runner and rollback procedure. Model inventory by store and SKU. Protect the last unit with an atomic conditional write or equivalent transaction. Define reservation expiry and enforce unique order attempts before enabling payment retries.

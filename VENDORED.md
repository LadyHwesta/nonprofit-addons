# Vendored OCA modules

Modules from the **Odoo Community Association** vendored here (at the repo root,
never under a directory named `vendor/` — that name on the addons path shadows
Bootstrap's `scss/vendor/` and breaks `web.assets_web`). Each keeps its own
upstream licence — **not** the repo's LGPL-3.

| Module | Upstream | Status |
| --- | --- | --- |
| `donation_base` | [OCA/donation](https://github.com/OCA/donation) `18.0` @ `3634b05` | **ported 18.0 → 19.0.** AGPL-3. See `LadyHwesta/donation` branch `19.0-mig-donation`. |
| `donation` | OCA/donation `18.0` @ `3634b05` | **ported 18.0 → 19.0.** AGPL-3. |

The OCA `donation` 19.0 branch was empty; these were forward-ported via the OCA
`[MIG]` cherry-pick workflow on a fork (`LadyHwesta/donation` →
`19.0-mig-donation`). The `[MIG]` commits there carry an `Assisted-by:` trailer
and are the basis for a future PR to OCA.

**19.0 migration changes** (see the `[MIG]` commit messages for detail):
`res.groups.category_id` → `res.groups.privilege` + `privilege_id`; `users` →
`user_ids`; `groups_id` → `group_ids`; `base.default_user` removed; search-view
`<group string="Group By">` → `<group>`; `product` search-view `type` filter
anchor gone; `account.account.deprecated` field removed; `target="inline"`
act_window value removed; `res.users` form `preferences` group →
`other_preferences`; `_sql_constraints` → `models.Constraint`; `self._cr` →
`self.env.cr`; demo `product.product_category_5` → `product_category_services`.

**`partner_match_or_create`** (also in OCA/donation 18.0) was **not** ported — it
is built entirely on `res.partner.title`, which Odoo 19 removed. It isn't a
dependency of the donation stack.

`readme/`, `i18n/` (~a dozen `.po` files) and `pyproject.toml` were stripped from
these copies. Nothing else was changed beyond the migration commits.

Tests: `donation` 6 + `donation_base` 8, green on Odoo 19 CE with demo data (run
with `--with-demo` locally; Odoo 19 no longer loads demo by default).

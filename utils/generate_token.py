# -*- coding: utf-8 -*-
app = env['core.api.application'].search([('name', '=', 'Demo API Application')], limit=1) or env['core.api.application'].create({'name': 'Demo API Application'})
token_res = env['core.api.token'].issue_for_application(app)
print('TOKEN:', token_res['access_token'])
env.cr.commit()

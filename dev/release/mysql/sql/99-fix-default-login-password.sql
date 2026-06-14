-- Keep the default OpenSPG web login usable for fresh Docker deployments.
-- username: openspg
-- password: openspg
UPDATE kg_user
SET token = '075Df6275475a739',
    salt = 'Ktu4O',
    dw_access_key = '18fa96c2dade75441850913685a41064f4c9472db2a400f44850aa076d746c51'
WHERE user_no = 'openspg';

-- Fallback administrator for deployments where browser autofill or copy/paste causes
-- the default account to be entered incorrectly.
-- username: admin
-- password: 123456
INSERT INTO kg_user
(gmt_create, gmt_modified, user_no, token, last_token, salt, gmt_last_token_disable,
 dw_access_id, dw_access_key, real_name, nick_name, email, domain_account, mobile, wx_account, config)
SELECT now(), now(), 'admin', 'Admin075Df627547', null, 'Adm01', null,
       null, 'ba5344759d4ed45e16bf13657b4675599ea9031201e854029e86b559a004d2aa',
       'admin', 'admin', null, 'admin', null, null, '{"useCurrentLanguage":"zh-CN"}'
WHERE NOT EXISTS (SELECT 1 FROM kg_user WHERE user_no = 'admin');

UPDATE kg_user
SET salt = 'Adm01',
    dw_access_key = 'ba5344759d4ed45e16bf13657b4675599ea9031201e854029e86b559a004d2aa',
    domain_account = 'admin',
    real_name = 'admin',
    nick_name = 'admin',
    config = '{"useCurrentLanguage":"zh-CN"}'
WHERE user_no = 'admin';

INSERT INTO kg_resource_permission
(gmt_create, gmt_modified, user_no, resource_id, role_id, resource_tag, status, expire_date)
SELECT now(), now(), 'admin', 0, 1, 'PLATFORM', '1', null
WHERE NOT EXISTS (
  SELECT 1 FROM kg_resource_permission
  WHERE user_no = 'admin' AND resource_id = 0 AND role_id = 1 AND resource_tag = 'PLATFORM'
);

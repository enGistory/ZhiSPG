-- Keep the default web login aligned with the white-label deployment.
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
SET token = 'Admin075Df627547',
    salt = 'Adm01',
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

INSERT INTO kg_resource_permission
(gmt_create, gmt_modified, user_no, resource_id, role_id, resource_tag, status, expire_date)
SELECT now(), now(), 'admin', source.resource_id, source.role_id, source.resource_tag, source.status, source.expire_date
FROM kg_resource_permission source
LEFT JOIN kg_resource_permission existing
  ON existing.user_no = 'admin'
 AND existing.resource_id = source.resource_id
 AND existing.role_id = source.role_id
 AND existing.resource_tag = source.resource_tag
WHERE source.user_no = 'openspg'
  AND existing.id IS NULL;

UPDATE kg_config SET user_no = 'admin' WHERE user_no = 'openspg';
UPDATE kg_ontology_release SET user_no = 'admin' WHERE user_no = 'openspg';
UPDATE kg_reason_session SET user_no = 'admin' WHERE user_no = 'openspg';
UPDATE kg_reason_task SET user_no = 'admin' WHERE user_no = 'openspg';
UPDATE kg_semantic_rule SET user_no = 'admin' WHERE user_no = 'openspg';

DELETE FROM kg_resource_permission WHERE user_no = 'openspg';
DELETE FROM kg_user WHERE user_no = 'openspg';

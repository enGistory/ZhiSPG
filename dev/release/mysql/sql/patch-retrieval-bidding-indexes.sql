SET NAMES utf8mb4;

INSERT INTO kg_retrieval (
  create_user, update_user, type, status, is_default, name, chinese_name,
  schema_desc, scenarios_desc, cost_desc, method_desc,
  extractor_desc, retriever_desc, module_path, class_name, method, extension, config
)
SELECT
  'system', 'system', 'kag', 'ENABLE', 'N', 'tender_document_index', '招标文件索引管理器',
  'Chunk(文本块): IndexType
     properties:
        content(内容): Text
          index: TextAndVector

TenderDocumentInfo(招标文件要素): IndexType
     properties:
        content(综合内容): Text
          index: TextAndVector
        projectName(项目名): Text
          index: TextAndVector
        projectCode(编号): Text
          index: TextAndVector
        unit(单位): Text
          index: TextAndVector
        amount(金额): Text
          index: TextAndVector
        regulation(法规): Text
          index: TextAndVector
     relations:
        sourceChunk(关联文本块): Chunk
        hasScoringItem(包含评分项): TenderScoringItem

TenderScoringItem(评分项): IndexType
     properties:
        itemName(评分项): Text
          index: TextAndVector
        scoringPoint(评分点): Text
          index: TextAndVector
        regulation(法规): Text
          index: TextAndVector
        amount(金额): Text
          index: TextAndVector
        unit(单位): Text
          index: TextAndVector
        content(综合内容): Text
          index: TextAndVector
     relations:
        sourceChunk(关联文本块): Chunk
        belongsTo(所属招标文件): TenderDocumentInfo',
  '**适用场景**: 招标文件解析、评分办法审查、法规依据定位、项目金额/编号/单位核验。

**检索流程**:
- 通过招标文件领域 schema 抽取评分项、评分点、法规、金额、项目名、编号、单位。
- 结合知识图谱检索、自由文本召回和向量文本块召回返回原文依据。',
  '复用 KAG 混合抽取与召回链路，成本接近基于文本块和图谱的混合索引；适合在招标文件需要结构化抽取时使用。',
  '面向招标文件字段构建领域图谱索引，并结合文本块召回定位原文依据。',
  extractor_desc, retriever_desc, 'bridge.spg_server_bridge', 'SPGServerBridge', 'tender_document_index', extension, config
FROM kg_retrieval WHERE name = 'kag_hybrid_index'
ON DUPLICATE KEY UPDATE
  chinese_name = VALUES(chinese_name),
  schema_desc = VALUES(schema_desc),
  scenarios_desc = VALUES(scenarios_desc),
  cost_desc = VALUES(cost_desc),
  method_desc = VALUES(method_desc),
  extractor_desc = VALUES(extractor_desc),
  retriever_desc = VALUES(retriever_desc),
  config = VALUES(config),
  status = 'ENABLE',
  gmt_modified = CURRENT_TIMESTAMP;

INSERT INTO kg_retrieval (
  create_user, update_user, type, status, is_default, name, chinese_name,
  schema_desc, scenarios_desc, cost_desc, method_desc,
  extractor_desc, retriever_desc, module_path, class_name, method, extension, config
)
SELECT
  'system', 'system', 'kag', 'ENABLE', 'N', 'bid_document_index', '投标文件索引管理器',
  'Chunk(文本块): IndexType
     properties:
        content(内容): Text
          index: TextAndVector

BidDocumentInfo(投标文件要素): IndexType
     properties:
        content(综合内容): Text
          index: TextAndVector
        projectFeature(项目特色): Text
          index: TextAndVector
        technicalAdvancement(技术方案先进): Text
          index: TextAndVector
        constructionDesignSplit(施组设计拆分): Text
          index: TextAndVector
        unit(单位): Text
          index: TextAndVector
     relations:
        sourceChunk(关联文本块): Chunk
        hasConstructionDesign(包含施组设计): ConstructionDesignPart

ConstructionDesignPart(施组设计拆分): IndexType
     properties:
        partName(拆分项): Text
          index: TextAndVector
        content(内容): Text
          index: TextAndVector
        unit(单位): Text
          index: TextAndVector
     relations:
        sourceChunk(关联文本块): Chunk
        belongsTo(所属投标文件): BidDocumentInfo',
  '**适用场景**: 投标文件解析、技术方案先进性检索、项目特色归纳、施工组织设计拆分和单位核验。

**检索流程**:
- 通过投标文件领域 schema 抽取项目特色、技术方案先进性、施组设计拆分、单位。
- 结合知识图谱检索、自由文本召回和向量文本块召回返回原文依据。',
  '复用 KAG 混合抽取与召回链路，成本接近基于文本块和图谱的混合索引；适合在投标文件需要结构化抽取时使用。',
  '面向投标文件字段构建领域图谱索引，并结合文本块召回定位原文依据。',
  extractor_desc, retriever_desc, 'bridge.spg_server_bridge', 'SPGServerBridge', 'bid_document_index', extension, config
FROM kg_retrieval WHERE name = 'kag_hybrid_index'
ON DUPLICATE KEY UPDATE
  chinese_name = VALUES(chinese_name),
  schema_desc = VALUES(schema_desc),
  scenarios_desc = VALUES(scenarios_desc),
  cost_desc = VALUES(cost_desc),
  method_desc = VALUES(method_desc),
  extractor_desc = VALUES(extractor_desc),
  retriever_desc = VALUES(retriever_desc),
  config = VALUES(config),
  status = 'ENABLE',
  gmt_modified = CURRENT_TIMESTAMP;

UPDATE kg_retrieval SET
  extractor_desc = '[{"type":"tender_document_extractor"}]',
  retriever_desc = '[{"type":"vector_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10},{"type":"text_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10}]',
  config = '{"extractor":[{"type":"tender_document_extractor"}],"retriever":[{"type":"vector_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10},{"type":"text_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10}]}',
  gmt_modified = CURRENT_TIMESTAMP
WHERE name = 'tender_document_index';

UPDATE kg_retrieval SET
  extractor_desc = '[{"type":"bid_document_extractor"}]',
  retriever_desc = '[{"type":"vector_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10},{"type":"text_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10}]',
  config = '{"extractor":[{"type":"bid_document_extractor"}],"retriever":[{"type":"vector_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10},{"type":"text_chunk_retriever","vectorize_model":{"type":"mock"},"search_api":{"type":"openspg_search_api"},"top_k":10}]}',
  gmt_modified = CURRENT_TIMESTAMP
WHERE name = 'bid_document_index';

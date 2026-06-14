# Copyright 2023 OpenSPG Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

# Local server image. Keep the published runtime dependencies and replace only the
# executable server jar built for this workspace.
FROM spg-registry.cn-hangzhou.cr.aliyuncs.com/spg/openspg-server:latest

EXPOSE 8887

ADD target/arks-sofaboot-0.0.1-SNAPSHOT-executable.jar /
COPY branding /tmp/openspg-branding
COPY scripts/patch_static_branding.py /tmp/patch_static_branding.py
RUN /home/admin/miniconda3/bin/python /tmp/patch_static_branding.py \
    --jar /arks-sofaboot-0.0.1-SNAPSHOT-executable.jar \
    --branding-dir /tmp/openspg-branding \
    && rm -rf /tmp/openspg-branding /tmp/patch_static_branding.py
COPY patches/kag/builder/component/vectorizer/batch_vectorizer.py /home/admin/miniconda3/lib/python3.10/site-packages/kag/builder/component/vectorizer/batch_vectorizer.py
COPY patches/kag/builder/component/extractor/bidding_document_extractor.py /home/admin/miniconda3/lib/python3.10/site-packages/kag/builder/component/extractor/bidding_document_extractor.py
COPY patches/kag/builder/component/__init__.py /home/admin/miniconda3/lib/python3.10/site-packages/kag/builder/component/__init__.py
COPY patches/kag/common/vectorize_model/openai_model.py /home/admin/miniconda3/lib/python3.10/site-packages/kag/common/vectorize_model/openai_model.py
COPY patches/kag/interface/common/model/chunk.py /home/admin/miniconda3/lib/python3.10/site-packages/kag/interface/common/model/chunk.py
COPY patches/kag/indexer/kag_index_manager.py /home/admin/miniconda3/lib/python3.10/site-packages/kag/indexer/kag_index_manager.py
RUN sed -i 's/level_map\[parent_level\]\.sub_chunks\.append(chunk)/level_map[parent_level].sub_chunks.append(chunk.id)/' /home/admin/miniconda3/lib/python3.10/site-packages/kag/builder/component/reader/pdf_reader.py
ENTRYPOINT ["java", "-jar", "arks-sofaboot-0.0.1-SNAPSHOT-executable.jar"]

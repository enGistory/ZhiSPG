# -*- coding: utf-8 -*-
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
from enum import Enum
from typing import Dict, Any
from kag.common.utils import generate_hash_id
import json


def _json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if value.__class__.__name__ == "Chunk" and hasattr(value, "id"):
        return value.id
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "to_dict"):
        try:
            return value.to_dict()
        except Exception:
            pass
    if hasattr(value, "id"):
        return value.id
    return str(value)


class ChunkTypeEnum(str, Enum):
    Table = "TABLE"
    Text = "TEXT"


class Chunk:
    def __init__(
        self,
        id: str,
        name: str,
        content: str,
        type: ChunkTypeEnum = ChunkTypeEnum.Text,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.content = content
        self.kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def hash_key(self):
        return generate_hash_id(f"{self.id}{self.name}{self.content}")

    def __str__(self):
        tmp = {
            "id": self.id,
            "name": self.name,
            "content": (
                self.content if len(self.content) <= 64 else self.content[:64] + " ..."
            ),
        }
        return f"<Chunk>: {tmp}"

    __repr__ = __str__

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "type": (
                self.type.value if isinstance(self.type, ChunkTypeEnum) else self.type
            ),
            "properties": json.dumps(_json_safe(self.kwargs), ensure_ascii=False),
        }

    @classmethod
    def from_dict(cls, input_: Dict[str, Any]):
        return cls(
            id=input_.get("id"),
            name=input_.get("name"),
            content=input_.get("content"),
            type=input_.get("type"),
            **json.loads(input_.get("properties", {}))
            if isinstance(input_.get("properties"), str)
            else input_.get("properties", {}),
        )


def dump_chunks(chunks, **kwargs):
    if kwargs.get("output_path"):
        with open(kwargs.get("output_path"), "w") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

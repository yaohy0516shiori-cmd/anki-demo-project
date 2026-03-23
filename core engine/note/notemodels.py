'''
### Note
- `id`：这条 note 实例自己的唯一标识
- `note_type_id`：指向所属 `NoteType` 的 id，用于解释 `fields`
- `fields`：这条 note 的具体内容
- `tags`：用户自定义标签
- `sort_field`：用于排序/列表显示的主字段，通常由 `fields` 派生
- `checksum`：由内容计算出的校验值，用于比较/查重/检测变化
- `created_at`：创建时间
- `updated_at`：最后更新时间
'''
from dataclasses import dataclass,field
from typing import List, Optional
from datetime import datetime,timezone 
# datetime 有module和class重名
import hashlib
from note.utils import calculate_checksum

@dataclass
class Note:
    # dataclass will generate __init__ method, so we don't need to define it
    note_type_id:int
    fields:List[str]
    note_id:Optional[int]=None
    tags:List[str]=field(default_factory=list)
    sort_field:Optional[str]=None
    checksum:Optional[str]=None
    created_at:Optional[str]=None
    updated_at:Optional[str]=None

    def __post_init__(self):
        self.__validation_content(self.fields, "fields")
        self.__validate_note_type_id(self.note_type_id)
        self.__validation_content(self.tags, "tags")
        if self.note_id is not None:
            self.__validate_id(self.note_id)

        if self.sort_field is None:
            self.sort_field=self.fields[0].strip() if self.fields else ""
            
        if self.checksum is None:
            self.checksum=calculate_checksum(self.fields)

        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        # if the created_at and updated_at are not set, set them to the current time
        if not self.created_at:
            self.created_at=now
        if not self.updated_at:
            self.updated_at=now



    @staticmethod
    def __validation_content(value,name:str):
        # validate the content of the value
        # if the fields are not legal, raise an error
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{name} is not a list of strings")
        return True
    
    @staticmethod
    def __validate_id(note_id:int):
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note id is not an integer or is not positive")
        return True

    @staticmethod
    def __validate_note_type_id(note_type_id:int):
        if not isinstance(note_type_id, int) or note_type_id <= 0:
            raise ValueError("Note type id is not an integer or is not positive")
        return True

    def refresh(self):
        self.updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.checksum=calculate_checksum(self.fields)
        self.sort_field=self.fields[0].strip() if self.fields else ""
    # don't need to define __repr__ method, dataclass will generate it
    # def __repr__(self):
    #     return f"Note(id={self.note_id}, note_type_id={self.note_type_id}, fields={self.fields}, 
    # tags={self.tags}, sort_field={self.sort_field}, 
    # checksum={self.checksum}, created_at={self.created_at}, updated_at={self.updated_at})"
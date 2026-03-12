'''
### Note Type
- `id`：该 note type 的唯一标识，用于让 `Note.note_type_id` 引用它
- `name`：给用户和开发者看的类型名称，不是 card front 内容
- `field_names`：定义该类型有哪些字段、字段顺序和字段名称
- `kind`：定义该类型的行为规则，例如 `basic`、`cloze`、`basic_reverse`

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
from typing import List, Optional
from datetime import datetime,timezone 
# datetime 有module和class重名
import hashlib

# 类命名首字母大写
class NoteType:
    def __init__(self,type_id:int,name:str,fields_names:List[str],kind:str):
        # 私有属性防止外部直接修改
        self.__type_id=type_id
        self.__name=name
        self.__field_names=list(fields_names)
        self.__kind=kind
    # Internal attributes and external attributes should be named separately.
    # otherwise, it will be confusing.
    @property
    def type_id(self):
        return self.__type_id
    @property
    def type_name(self):
        return self.__name
    @property
    def field_names(self):
        return list(self.__field_names)
    @property
    def type_kind(self):
        return self.__kind
    
class Note():
    def __init__(
        self,
        note_type_id:int,
        fields:List[str],
        note_id:Optional[int]=None,
        tags:Optional[List[str]]=None):
        # __init__ will be called when a new note is created
        self.__id=None # initialize as None, then set it in set_id method
        if note_id is not None:
            self.set_id(note_id)
        # repository will generate id if user doesn't provide one
        self.__note_type_id=note_type_id
        self.__validation_content(fields, "fields")
        self.__validation_content(tags if tags is not None else [], "tags")
        self.__fields=list(fields) 
        # shallow copy in order to avoid modifying the original list by mistake
        self.__tags=list(tags) if tags is not None else []
        self.__sort_field=fields[0].strip() if fields else ""  
        self.__checksum=self.__calculate_checksum(self.__fields)
        self.__created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat() 
        # iso, microsecond=0
        self.__updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    
    def __calculate_checksum(self,fields:List[str]):
        # generate hash from fields, hashlib is more secure than hash for long-term storage
        new_fields="|".join(field.strip() for field in fields)
        # to differentiate ['a','b','c'] and ['a','bc']
        return hashlib.sha256(new_fields.encode('utf-8')).hexdigest()

    def __validation_content(self,value,name:str):
        # validate the content of the value
        # if the fields are not legal, raise an error
        if not isinstance(value, list):
            raise ValueError(f"{name} is not a list")
        if not all(isinstance(item, str) for item in value):
            raise ValueError(f"{name} is not a list of strings")

    def __judge_legal(self,fields:List[str]):
        # not put in here, should be in service layer
        # we need note type to judge the legal of the fields, 
        # if the fields are not legal, raise an error, but how?
        return 
        
    def update(self,fields:List[str]):
        self.__validation_content(fields, "fields")
        # change if checksum is not the same
        # different from __init__ Instance attribute, here is a method to update the note
        if len(fields) != len(self.__fields):
            # we can use __judge_legal to judge the legal of the fields, 
            # but it should be in service layer
            raise ValueError("Input is not legal")
        elif self.__checksum != self.__calculate_checksum(fields):
            self.__checksum=self.__calculate_checksum(fields)
            self.__fields=list(fields)
            self.__sort_field = self.__fields[0].strip() if self.__fields else ""
            self.__updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            return True 
        else:
            return False 

    def add_tag(self,tag):
        if not isinstance(tag, str):
            raise TypeError("Tag is not a string")
        if not isinstance(tag, str):
            raise TypeError("Tag is not a string")
        if tag in self.__tags: 
            # too simple, we don't use any algorithm to check if the tag is already exists. 
            # don't expect users to obey the rules.
            raise ValueError("Tag already exists")
        elif not tag.strip():
            raise ValueError("Tag is empty")
        else:
            self.__tags.append(tag)
            self.__updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            return True

    def set_id(self,note_id):
        # When a user creates a Note, the id can initially be None. 
        # When storing in the storage layer/repository, assign an ID to it. 
        # Once the setting is completed, it cannot be changed anymore.
        if self.__id is not None:
            raise ValueError("Note id is already set")
        elif not isinstance(note_id, int):
            raise ValueError("Note id is not an integer")
        elif note_id <= 0:
            raise ValueError("Note id is not positive")
        else:
            self.__id=note_id
            return True

    # any decorater to improve the code? @property is a good choice
    @property
    def note_id(self):
        return self.__id
    @property
    def note_type_id(self):
        return self.__note_type_id # only know the type id, not the type object
    @property
    def field_content(self):
        return self.__fields
    @property
    def sort_field(self):
        return self.__sort_field
    @property
    def checksum_hash(self):
        return self.__checksum
    @property
    def created_time(self):
        return self.__created_at
    @property
    def updated_time(self):
        return self.__updated_at
    @property
    def user_tags(self):
        return list(self.__tags)
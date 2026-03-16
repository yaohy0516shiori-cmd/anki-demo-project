'''
### NoteType
- `id`：这条 note type 实例自己的唯一标识
- `name`：这条 note type 的名称
- `field_names`：这条 note type 的字段名称
- `kind`：这条 note type 的类型
'''

from typing import List, Optional
from datetime import datetime,timezone 
# datetime 有module和class重名
import hashlib# class name should be capitalized

class NoteType:
    def __init__(self,type_id:int,name:str,field_names:List[str],kind:str):
        # private attributes to prevent external modification
        # __init__ will be called when a new note type is created
        # judge the type of the arguments
        kind_list=["basic", "cloze", "basic_reverse"]
        if not isinstance(type_id, int):
            raise ValueError("Type id is not an integer")
        if name is None or name.strip() == "" or not isinstance(name, str):
            raise TypeError("Name is not a string")
        if not isinstance(field_names, list):
            raise TypeError("Field names is not a list")
        if not all(isinstance(item, str) for item in field_names):
            raise TypeError("Field names is not a list of strings")
        if kind not in kind_list:
            raise TypeError("Kind is not legal")
        self.__type_id=type_id
        self.__name=name
        self.__field_names=list(field_names)
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
    def __repr__(self):
        return f"NoteType(id={self.__type_id}, name={self.__name}, field_names={self.__field_names}, kind={self.__kind})"
    def to_dict(self):
        return {
            "id": self.__type_id,
            "name": self.__name,
            "field_names": self.__field_names,
            "kind": self.__kind
        }
    # what is cls?
    @classmethod
    def from_dict(cls, data:dict):
        return cls(data["id"], data["name"], data["field_names"], data["kind"])
    
    
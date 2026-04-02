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
    def __init__(self,note_type_id:int | None,name:str,field_names:List[str],kind:str):
        '''
        Validate and create a note type
        Args:
            note_type_id: The id of the note type
            name: The name of the note type
            field_names: The fields of the note type
            kind: The kind of the note type
        Returns:
            A NoteType object
        private attributes to prevent external modification
        __init__ will be called when a new note type is created
        judge the type of the arguments
        '''
        kind_list=["basic", "cloze", "basic_reverse"]
        if note_type_id is not None and not isinstance(note_type_id, int):
            raise ValueError("Type id is an integer")
        if name is None or name.strip() == "" or not isinstance(name, str):
            raise TypeError("Name is a string")
        if not isinstance(field_names, list):
            raise TypeError("Field names is a list")
        if not all(isinstance(item, str) for item in field_names):
            raise TypeError("Field names is a list of strings")
        if kind not in kind_list:
            raise TypeError("Kind is not legal")
        self.__note_type_id=note_type_id if note_type_id is not None else None
        self.__name=name.strip()
        self.__field_names=list(field_names)
        self.__kind=kind.strip()
    # Internal attributes and external attributes should be named separately.
    # otherwise, it will be confusing.
    @property
    def note_type_id(self):
        # Return note type id, this is a property
        return self.__note_type_id
    @property
    def name(self):
        # Return note type name, this is a property
        return self.__name
    @property
    def field_names(self):
        # Return note type field names, this is a property
        return list(self.__field_names)
    @property
    def kind(self):
        # Return note type kind, this is a property
        return self.__kind
    def __repr__(self):
        # Return a string representation of the note type
        return f"NoteType(id={self.__note_type_id}, name={self.__name}, field_names={self.__field_names}, kind={self.__kind})"
    def to_dict(self):
        # Return a dictionary representation of the note type
        return {
            "note_type_id": self.__note_type_id,
            "name": self.__name,
            "field_names": self.__field_names,
            "kind": self.__kind
        }
    @classmethod
    def from_dict(cls, data:dict):
        # Create a note type from a dictionary
        return cls(data["note_type_id"], data["name"], data["field_names"], data["kind"])
    
    
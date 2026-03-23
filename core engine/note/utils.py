# tools
import hashlib
from typing import List

def calculate_checksum(fields:List[str]):
    # generate hash from fields, hashlib is more secure than hash for long-term storage
    new_fields="|".join(field.strip() for field in fields)
    # to differentiate ['a','b','c'] and ['a','bc']
    return hashlib.sha256(new_fields.encode('utf-8')).hexdigest()
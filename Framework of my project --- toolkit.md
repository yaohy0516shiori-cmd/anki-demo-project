# Framework of my project --- toolkit

# Core engine

## note/

### 1.`notemodels.py`

- **__post_init_**(*self*) note 的基础属性
- note 自身合法性校验
  1. **__validation_content**
  2. **__validate_id**
  3. **__validate_note_type_id**
- 默认值生成
- `sort_field`
- `checksum`
- 时间戳
- `refresh()`

------

### 2. `repository.py`

- `add_note`
- `get_note`
- `update_note`
- `delete_note`
- `get_all_notes`

------

### 3. `service.py`

- `create_note`
- `get_note`
- `list_notes`
- `update_note`
- `delete_note`
- `is_duplicate`

### 4.utils.py

​	checksum()

### 5.expectations.py

## Note_type/

### 1. `notetype.py`

- note_type_id
- name 
- field_names 
- kind


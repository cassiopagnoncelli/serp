# Record

Record is an async object model mapping built on top of Tortoise ORM.

It aims to provide higher-level abstractions similar to Ruby on Rails Active
Model and Active Record.

## Features

### ActiveModel - Class Methods

| Feature | Status |
|---------|--------|
| Callbacks: {before,after}_{create,update,destroy,validation} | Tortoise |
| Validations: validates_*, validate | Pydantic |

### ActiveModel - Instance Methods

| Feature | Status |
|---------|--------|
| Conversion: persisted?, new_record? | N/A |
| Dirty: changed? | N/A |
| Callbacks: run_callbacks | N/A |

### ActiveRecord - Class Methods

| Feature | Status |
|---------|--------|
| Finder: find, find_by | - |
| Finder: first, last | ✅ **Available** |
| Query: where, order, limit, offset, group, having, joins*, includes, eager_load, preload, distinct | Tortoise |
| Batch Processing: find_each, find_in_batches | ✅  **Avaiable** |
| CRUD: create, update, destroy, destroy_all, delete, delete_all | Tortoise |
| Associations: belongs_to, has_one, has_many, has_and_belongs_to_many | Tortoise |
| Query Methods: scope, default_scope, pluck, ids, exists | Tortoise |
| Validations: validates_{presence,uniqueness,format,length}_of, validate | Pydantic |
| Callbacks: {before,after}_{validation,save,create,update,destroy} | Tortoise |
| Calculations: count, average, minimum, maximum, sum | Tortoise |

### ActiveRecord - Instance Methods

| Feature | Status |
|---------|--------|
| CRUD: save, update, destroy, delete | ✅ **Available** |
| Reloading: reload | ✅ **Available** |
| Timestamps: touch | ✅ **Available** |
| Serialization: to_json, serializable_hash | ✅ **Available** |


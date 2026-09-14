# db Structure

## Base Models (applied to most entities)

All entities inherit one or more of these base behaviors:

| Model                    | Fields added                                      |
|--------------------------|---------------------------------------------------|
| `UUIDModel`              | `public_id: UUID` (unique, indexed, non-editable) |
| `CreatedModel`           | `created_at: DateTime`                            |
| `UpdatedModel`           | `updated_at: DateTime`                            |
| `TimeStampedModel`       | `created_at` + `updated_at`                       |
| `SoftDeleteModel`        | `deleted_at: DateTime?`                           |
| `TimeStampedSoftDeleteModel` | `created_at` + `updated_at` + `deleted_at`    |

---

## Domains

### Auth (built-in)

**User** (Django's `auth.User`)
- `id: int` (PK)
- `public_id: UUID`
- `external_id: str`
- *(standard Django auth fields)*

---

### Workplace

**Workplace**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `deleted_at: DateTime?`
- `name: string` (max 200)
- `slug: string` (unique)
- `photo: string?` (file path)
- `cover_style: string` (max 500, cor/gradiente CSS ou URL de imagem)
- `cover_credit: json?` (atribuição da capa — ex.: foto do Unsplash)
- `is_active: boolean` (default: true)
- `invite_key: string` (max 8, unique)
- `storage_used: bigint` (default: 0)
- `storage_limit: bigint` (default: 5 GB)
- `ai_usage_tokens: bigint` (default: 0)
- `ai_limit_tokens: bigint` (default: 1,000,000)

**WorkplaceMember**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `workplace_id → Workplace` (CASCADE)
- `user_id → User` (CASCADE)
- `role: enum` (`owner` | `manager` | `designer`, default: `designer`)
- *unique constraint: (workplace_id, user_id)*

---

### Form

**Form**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `workplace_id → Workplace?` (CASCADE, nullable)
- `title: string` (max 255)
- `description: text`
- `is_published: boolean` (default: false)
- `cover_image: string?` (file path)
- `cover_style: string` (max 500, cor/gradiente CSS ou URL de imagem)
- `cover_credit: json?` (atribuição da capa — ex.: foto do Unsplash)
- `require_auth: boolean` (default: false)
- `require_identity: boolean` (default: false)
- `grid_columns: smallint` (default: 1)

**FormPage**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `form_id → Form` (CASCADE)
- `title: string` (max 255, optional)
- `description: text` (optional)
- `order: smallint` (default: 0)
- *unique constraint: (form_id, order)*

**FormBlock**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `form_id → Form` (CASCADE)
- `page_id → FormPage?` (SET NULL, nullable)
- `title: string` (max 255)
- `type: enum` (`text` | `email` | `number` | `time` | `date` | `file` | `choice` | `select`)
- `required: boolean` (default: false)
- `order: int` (default: 0)
- `config: json` (default: `{}`)
- `col_span: smallint` (default: 0)
- `col_stMedia: smallint` (default: 0)
- `condition: json` (default: `{}`)
- `client_id: string` (max 64, optional)
- *unique constraint: (form_id, page_id, order)*

**FormResponse**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `form_id → Form` (CASCADE)
- `respondent_email: string` (optional)
- `respondent_phone: string` (max 20, optional)

**FormAnswer**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `response_id → FormResponse` (CASCADE)
- `block_id → FormBlock` (CASCADE)
- `value: json`

**FormAnswerFile**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `answer_id → FormAnswer` (CASCADE)
- `file: string` (file path)

---

### Task

**TaskTag**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `workplace_id → Workplace?` (CASCADE, nullable)
- `name: string` (max 50)
- `color: string` (max 7, hex, default: `#5CFCD4`)

**Task**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `deleted_at: DateTime?`
- `workplace_id → Workplace?` (CASCADE, nullable)
- `created_by_id → User?` (CASCADE, nullable)
- `title: string` (max 200)
- `description: text`
- `type: enum` (`Media` | `post` | `meeting` | `content` | `other`)
- `status: enum` (`todo` | `in_progress` | `in_review` | `done` | `cancelled`, default: `todo`)
- `priority: enum` (`low` | `medium` | `high` | `urgent`, default: `medium`)
- `origin: enum` (`internal` | `external`, default: `internal`)
- `deadline: date?`
- `completed_at: DateTime?`
- *indexes: (workplace_id, deleted_at), (workplace_id, status_id, deleted_at)*

**Task_Assignees** *(many-to-many join table)*
- `task_id → Task`
- `user_id → User`

**Task_Tags** *(many-to-many join table)*
- `task_id → Task`
- `tag_id → TaskTag`

**SubTask** (Subtask)
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `task_id → Task` (CASCADE)
- `assignee_id → User?` (SET NULL, nullable)
- `title: string` (max 200)
- `is_done: boolean` (default: false)

---

### Media

**Media**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `task_id → Task` (CASCADE)
- `designer_id → User?` (SET NULL, nullable)
- `title: string` (max 255, optional)
- `notes: text`
- `is_approved: boolean` (default: false)
- `share_token: UUID` (unique, indexed)

**MediaVersion**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `media_id → Media` (CASCADE)
- `number: smallint` (default: 1, indexed)
- `type: enum` (`1=image` | `2=video` | `3=file` | `4=link` | `5=text`, default: `1`)
- `file: string` (file path, optional)
- *unique constraint: (media_id, number)*

**MediaFeedback**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `media_id → Media` (CASCADE)
- `version_id → MediaVersion?` (CASCADE, nullable)
- `given_by_id → User` (CASCADE)
- `decision: enum` (`1=like` | `2=dislike`, default: `1`)
- `notes: text`
- *unique constraint: (media_id, version_id, given_by_id)*

**MediaComment**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `media_id → Media` (CASCADE)
- `version_id → MediaVersion?` (CASCADE, nullable)
- `author_id → User?` (CASCADE, nullable)
- `content: text`

---

### Inbox

**Inbox**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `user_id → User` (CASCADE)
- `type: enum` (`1=system` | `2=order` | `3=message`, default: `1`)
- `title: string` (max 255)
- `message: text`
- `is_read: boolean` (default: false)
- *indexes: (user_id, is_read), (type)*

---

### Sticky

**Sticky**
- `id: int` (PK)
- `public_id: UUID`
- `created_at: DateTime`
- `updated_at: DateTime`
- `deleted_at: DateTime?`
- `workplace_id → Workplace` (CASCADE)
- `created_by_id → User` (CASCADE)
- `visibility: enum` (`private` | `workplace`, default: `private`)
- `color: string` (max 7, hex, default: `#FEE440`)
- `text: text`
- *indexes: (workplace_id, deleted_at), (workplace_id, visibility, deleted_at), (workplace_id, created_by_id, deleted_at)*

---

## Entity Relationship Summary

```
User
 ├── Profile (1:1)
 ├── WorkplaceMember (1:N) → Workplace
 ├── Task.created_by (1:N)
 ├── Task.assignees (M:N)
 ├── SubTask.assignee (1:N)
 ├── Media.designer (1:N)
 ├── MediaFeedback.given_by (1:N)
 ├── MediaComment.author (1:N)
 ├── Inbox (1:N)
 └── Sticky.created_by (1:N)

Workplace
 ├── WorkplaceMember (1:N)
 ├── Form (1:N)
 ├── TaskTag (1:N)
 ├── Task (1:N)
 └── Sticky (1:N)

Form
 ├── FormPage (1:N)
 ├── FormBlock (1:N) → FormPage?
 └── FormResponse (1:N)
      └── FormAnswer (1:N) → FormBlock
           └── FormAnswerFile (1:N)

Task
 ├── SubTask (1:N)
 ├── Task_Assignees (M:N → User)
 ├── Task_Tags (M:N → TaskTag)
 └── Media (1:N)
      ├── MediaVersion (1:N)
      ├── MediaFeedback (1:N) → MediaVersion?
      └── MediaComment (1:N) → MediaVersion?
```

# API Testing Guide (Postman)

**Base URL:** `http://127.0.0.1:8000/api`

---

## AUTH ENDPOINTS

---

### 1. Register

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/register/` |
| **Auth** | None |

**Body (raw JSON):**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "StrongPass123!",
    "password2": "StrongPass123!"
}
```

**Response (201):**
```json
{
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        ...
    },
    "tokens": {
        "access": "<access_token>",
        "refresh": "<refresh_token>"
    }
}
```

---

### 2. Login

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/login/` |
| **Auth** | None |

**Body (raw JSON):**
```json
{
    "username": "testuser",
    "password": "StrongPass123!"
}
```

**Response (200):** Returns `user` + `tokens` (same as register).

---

### 3. Refresh Token

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/token/refresh/` |
| **Auth** | None |

**Body:**
```json
{
    "refresh": "<refresh_token>"
}
```

**Response (200):**
```json
{
    "access": "<new_access_token>",
    "refresh": "<new_refresh_token>"
}
```

---

### 4. View / Update Profile

| | |
|---|---|
| **Method** | `GET` / `PUT` / `PATCH` |
| **URL** | `/api/profile/` |
| **Auth** | Bearer Token |

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**PUT body:**
```json
{
    "username": "testuser",
    "email": "new@example.com",
    "phone": "0987654321",
    "bio": "Updated bio",
    "first_name": "John",
    "last_name": "Doe"
}
```

---

### 5. Change Password

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/change-password/` |
| **Auth** | Bearer Token |

**Body:**
```json
{
    "old_password": "StrongPass123!",
    "new_password": "NewStrongPass456!"
}
```

**Response (200):**
```json
{
    "detail": "Password changed successfully."
}
```

---

## TASK ENDPOINTS

All task endpoints require `Authorization: Bearer <access_token>`.

---

### 6. List All Tasks

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/tasks/` |
| **Auth** | Bearer Token |

**Response (200):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Study Django",
            "description": "Learn DRF",
            "status": "pending",
            "priority": "high",
            "due_date": "2026-09-20",
            "created_at": "2026-09-19T...",
            "updated_at": "2026-09-19T..."
        },
        {
            "id": 2,
            "title": "Buy groceries",
            "description": "",
            "status": "completed",
            "priority": "low",
            "due_date": "2026-09-21",
            "created_at": "2026-09-19T...",
            "updated_at": "2026-09-19T..."
        }
    ]
}
```

---

### 7. Create Task

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/tasks/` |
| **Auth** | Bearer Token |

**Body:**
```json
{
    "title": "Study Django",
    "description": "Learn Django REST Framework",
    "status": "pending",
    "priority": "high",
    "due_date": "2026-09-20"
}
```

**Response (201):**
```json
{
    "id": 1,
    "title": "Study Django",
    "description": "Learn Django REST Framework",
    "status": "pending",
    "priority": "high",
    "due_date": "2026-09-20",
    "created_at": "2026-09-19T...",
    "updated_at": "2026-09-19T..."
}
```

---

### 8. Get Single Task

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/tasks/<id>/` |
| **Auth** | Bearer Token |

**Response (200):** Single task object.

**Response (404):** If task doesn't exist or belongs to another user.

---

### 9. Update Task (Full)

| | |
|---|---|
| **Method** | `PUT` |
| **URL** | `/api/tasks/<id>/` |
| **Auth** | Bearer Token |

**Body (all fields required):**
```json
{
    "title": "Study Django",
    "description": "Learn DRF and JWT",
    "status": "in_progress",
    "priority": "medium",
    "due_date": "2026-09-25"
}
```

---

### 10. Update Task (Partial)

| | |
|---|---|
| **Method** | `PATCH` |
| **URL** | `/api/tasks/<id>/` |
| **Auth** | Bearer Token |

**Body (only fields to update):**
```json
{
    "status": "in_progress"
}
```

---

### 11. Delete Task

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/api/tasks/<id>/` |
| **Auth** | Bearer Token |

**Response (204):** No content.

---

### 12. Mark Task Complete

| | |
|---|---|
| **Method** | `PATCH` |
| **URL** | `/api/tasks/<id>/complete/` |
| **Auth** | Bearer Token |

**Body:** Empty (no body needed)

**Response (200):**
```json
{
    "id": 1,
    "title": "Study Django",
    "description": "Learn DRF",
    "status": "completed",
    "priority": "high",
    "due_date": "2026-09-20",
    "created_at": "2026-09-19T...",
    "updated_at": "2026-09-19T..."
}
```

---

### 13. Dashboard

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/tasks/dashboard/` |
| **Auth** | Bearer Token |

**Response (200):**
```json
{
    "total_tasks": 12,
    "pending": 5,
    "in_progress": 3,
    "completed": 4
}
```

---

## PERMISSIONS

Each user can only see **their own** tasks. If User A tries to access User B's task by ID:

```
GET /api/tasks/5/
```

Response:
```json
{
    "detail": "Not found."
}
```

Status: `404 Not Found`

---

## Postman Setup Tips

1. **After login/register**, copy the `access` token.

2. **Set Authorization** on protected requests:
   - Type: `Bearer Token`
   - Token: `<access_token>`

3. **Auto-save token:** In Login request, go to **Tests** tab:
   ```javascript
   var jsonData = pm.response.json();
   pm.environment.set("access_token", jsonData.tokens.access);
   pm.environment.set("refresh_token", jsonData.tokens.refresh);
   ```
   Then use `{{access_token}}` in headers.

4. **Content-Type:** Always `application/json` for POST/PUT/PATCH.

---

## Full Testing Flow

```
1.  POST /api/register/            → get user + tokens
2.  GET  /api/profile/             → verify profile
3.  PUT  /api/profile/             → update profile
4.  POST /api/tasks/               → create task 1
5.  POST /api/tasks/               → create task 2
6.  GET  /api/tasks/               → list all tasks
7.  GET  /api/tasks/1/             → get single task
8.  PATCH /api/tasks/1/            → update task partially
9.  PATCH /api/tasks/1/complete/   → mark task complete
10. GET  /api/tasks/dashboard/     → view stats
11. DELETE /api/tasks/2/           → delete task
12. POST /api/change-password/     → change password
13. POST /api/token/refresh/       → refresh token
```

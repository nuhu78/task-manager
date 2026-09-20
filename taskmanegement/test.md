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
    "password2": "StrongPass123!",
    "role": "manager"
}
```

**Response (201):**
```json
{
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "manager",
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
    "last_name": "Doe",
    "role": "manager"
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

## RBAC ENDPOINTS (Manager Only)

All endpoints below require `Authorization: Bearer <access_token>` and the user must have `role: "manager"`.

---

### 6. List Employees

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/employees/` |
| **Auth** | Bearer Token (Manager only) |

**Response (200):**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "username": "emp1",
            "email": "emp1@example.com",
            "phone": "1234567890",
            "role": "employee"
        },
        {
            "id": 3,
            "username": "emp2",
            "email": "emp2@example.com",
            "phone": "",
            "role": "employee"
        }
    ]
}
```

---

### 7. Create Team

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/teams/` |
| **Auth** | Bearer Token (Manager only) |

**Body:**
```json
{
    "name": "Frontend Team",
    "description": "Handles all frontend development"
}
```

**Response (201):**
```json
{
    "id": 1,
    "name": "Frontend Team",
    "description": "Handles all frontend development",
    "manager": 1,
    "members": [],
    "member_count": 0,
    "created_at": "2026-09-19T..."
}
```

---

### 8. List My Teams

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/teams/` |
| **Auth** | Bearer Token (Manager only) |

**Response (200):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Frontend Team",
            "description": "Handles all frontend development",
            "manager": 1,
            "member_count": 3,
            "created_at": "2026-09-19T..."
        },
        {
            "id": 2,
            "name": "Backend Team",
            "description": "Backend development team",
            "manager": 1,
            "member_count": 2,
            "created_at": "2026-09-19T..."
        }
    ]
}
```

---

### 9. Get Single Team

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/teams/<id>/` |
| **Auth** | Bearer Token (Manager only) |

**Response (200):**
```json
{
    "id": 1,
    "name": "Frontend Team",
    "description": "Handles all frontend development",
    "manager": 1,
    "members": [
        {
            "id": 1,
            "employee": {
                "id": 2,
                "username": "emp1",
                "email": "emp1@example.com",
                "phone": "1234567890",
                "role": "employee"
            },
            "joined_at": "2026-09-19T..."
        }
    ],
    "member_count": 1,
    "created_at": "2026-09-19T..."
}
```

---

### 10. Update Team

| | |
|---|---|
| **Method** | `PUT` / `PATCH` |
| **URL** | `/api/teams/<id>/` |
| **Auth** | Bearer Token (Manager only) |

**Body (PATCH):**
```json
{
    "name": "Frontend Dev Team",
    "description": "Updated description"
}
```

**Response (200):** Updated team object.

---

### 11. Delete Team

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/api/teams/<id>/` |
| **Auth** | Bearer Token (Manager only) |

**Response (204):** No content.

---

### 12. Assign Employee to Team

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/teams/<id>/assign/` |
| **Auth** | Bearer Token (Manager only) |

**Body:**
```json
{
    "employee_id": 2
}
```

**Response (201):**
```json
{
    "id": 1,
    "employee": {
        "id": 2,
        "username": "emp1",
        "email": "emp1@example.com",
        "phone": "1234567890",
        "role": "employee"
    },
    "joined_at": "2026-09-19T..."
}
```

---

### 13. Remove Employee from Team

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/api/teams/<id>/assign/` |
| **Auth** | Bearer Token (Manager only) |

**Body:**
```json
{
    "employee_id": 2
}
```

**Response (204):** No content.

---

## TASK ENDPOINTS

All task endpoints require `Authorization: Bearer <access_token>`.

---

### 14. List All Tasks

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

### 15. Create Task

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

### 16. Get Single Task

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/tasks/<id>/` |
| **Auth** | Bearer Token |

**Response (200):** Single task object.

---

### 17. Update Task (Full)

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

### 18. Update Task (Partial)

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

### 19. Delete Task

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/api/tasks/<id>/` |
| **Auth** | Bearer Token |

**Response (204):** No content.

---

### 20. Mark Task Complete

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

### 21. Dashboard

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

| Endpoint | Manager | Employee |
|----------|---------|----------|
| `/api/employees/` | ✅ | ❌ |
| `/api/teams/` (CRUD) | ✅ | ❌ |
| `/api/teams/<id>/assign/` | ✅ | ❌ |
| `/api/tasks/` | ✅ (own) | ✅ (own) |
| `/api/tasks/<id>/` | ✅ (own) | ✅ (own) |

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
1.  POST /api/register/            → register manager (role: "manager")
2.  POST /api/register/            → register employee (role: "employee")
3.  POST /api/login/               → login as manager, get token
4.  GET  /api/employees/           → list all employees
5.  POST /api/teams/               → create team
6.  GET  /api/teams/               → list teams
7.  POST /api/teams/1/assign/      → assign employee to team
8.  GET  /api/teams/1/             → view team with members
9.  DELETE /api/teams/1/assign/    → remove employee from team
10. PUT  /api/teams/1/             → update team
11. DELETE /api/teams/1/           → delete team
12. POST /api/tasks/               → create task
13. GET  /api/tasks/               → list tasks
14. PATCH /api/tasks/1/            → update task
15. PATCH /api/tasks/1/complete/   → mark complete
16. GET  /api/tasks/dashboard/     → view stats
17. DELETE /api/tasks/1/           → delete task
```

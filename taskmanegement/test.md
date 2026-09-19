# API Testing Guide (Postman)

**Base URL:** `http://127.0.0.1:8000/api`

---

## 1. Register

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/register/` |
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

**Expected Response (201):**
```json
{
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": "",
        "bio": "",
        "profile_picture": null,
        "first_name": "",
        "last_name": "",
        "date_joined": "2026-09-19T..."
    },
    "tokens": {
        "access": "<access_token>",
        "refresh": "<refresh_token>"
    }
}
```

---

## 2. Login

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/login/` |
| **Auth** | None |

**Body (raw JSON):**
```json
{
    "username": "testuser",
    "password": "StrongPass123!"
}
```

**Expected Response (200):**
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

## 3. Refresh Token

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/token/refresh/` |
| **Auth** | None |

**Body (raw JSON):**
```json
{
    "refresh": "<refresh_token>"
}
```

**Expected Response (200):**
```json
{
    "access": "<new_access_token>",
    "refresh": "<new_refresh_token>"
}
```

---

## 4. View / Update Profile

| | |
|---|---|
| **Method** | `GET` or `PUT` / `PATCH` |
| **URL** | `http://127.0.0.1:8000/api/profile/` |
| **Auth** | Bearer Token |

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**GET** — Returns current user profile.

**PUT** — Update full profile:
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

## 5. Change Password

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/change-password/` |
| **Auth** | Bearer Token |

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
    "old_password": "StrongPass123!",
    "new_password": "NewStrongPass456!"
}
```

**Expected Response (200):**
```json
{
    "detail": "Password changed successfully."
}
```

---

## Postman Setup Tips

1. **After login/register**, copy the `access` token from the response.

2. **Set Authorization header** on protected requests:
   - Type: `Bearer Token`
   - Token: `<access_token>`

3. **Auto-save token (optional):** In Login request, go to **Tests** tab and add:
   ```javascript
   var jsonData = pm.response.json();
   pm.environment.set("access_token", jsonData.tokens.access);
   pm.environment.set("refresh_token", jsonData.tokens.refresh);
   ```
   Then use `{{access_token}}` in Authorization headers.

4. **Content-Type:** Always set `Content-Type: application/json` for POST/PUT requests.

---

## Testing Order

```
1. POST /api/register/     → get user + tokens
2. POST /api/profile/      → view profile (use access token)
3. PUT  /api/profile/      → update bio, phone, etc.
4. POST /api/change-password/ → change password
5. POST /api/token/refresh/   → refresh expired token
```

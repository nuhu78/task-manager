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
    "password2": "StrongPass123!",
    "phone": "1234567890",
    "bio": "Hello world"
}
```

**Expected Response (201):**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "phone": "1234567890",
    "bio": "Hello world",
    "profile_picture": null,
    "first_name": "",
    "last_name": "",
    "date_joined": "2026-09-19T..."
}
```

---

## 2. Get JWT Token (Login)

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

**Expected Response (200):** Returns user info (same as register response).

---

## 3. Get JWT Access + Refresh Token

To use SimpleJWT's token pair (for refresh flow):

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/api/token/refresh/` |
| **Auth** | None |

**Body (raw JSON):**
```json
{
    "refresh": "<refresh_token_here>"
}
```

**Expected Response (200):**
```json
{
    "access": "<new_access_token>",
    "refresh": "<new_refresh_token>"
}
```

> **Note:** To get the initial token pair, add `TokenObtainPairView` to your urls (see below), then POST to `/api/token/` with `username` and `password`.

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

1. **Set environment variable:** Create a Postman environment with `base_url` = `http://127.0.0.1:8000/api` and `token` = `<your_access_token>`.

2. **Auto-save token:** In the Login request, go to **Tests** tab and add:
   ```javascript
   var jsonData = pm.response.json();
   pm.environment.set("token", jsonData.access);
   ```

3. **Use variable in headers:** For authenticated requests, set:
   ```
   Authorization: Bearer {{token}}
   ```

4. **Content-Type:** Always set header `Content-Type: application/json` for POST/PUT requests.

# 🚀 FastAPI JWT Auth + CRUD API Example

This project is a simple FastAPI-based API that demonstrates:

* User registration and login with **JWT authentication**
* Token refreshing with **access/refresh tokens**
* Basic **CRUD** (Create, Read, Update, Delete) operations on items
* Secured routes using JWT
* Postman testing support

---

## 🧰 Requirements

* Python 3.8+
* FastAPI
* Uvicorn
* Passlib
* python-jose
* Pydantic

Install dependencies:

```bash
pip install fastapi uvicorn python-jose passlib[bcrypt]
```

---

## ▶️ How to Run the Server

```bash
uvicorn main:app --reload
```

This will start the API at `http://127.0.0.1:8000`.

---

## 🔑 JWT Authentication Flow Explained

### 🔐 Access Token

* A **short-lived** token (15 minutes) used to authenticate API requests.
* Must be included in the `Authorization` header as:

  ```
  Bearer <access_token>
  ```

### ♻️ Refresh Token

* A **longer-lived** token (7 days) used to obtain a new access token **after it expires**.
* Sent to the `/refresh` endpoint to get new tokens.

---

## 📬 How to Test This in Postman

### Step 1: Signup

**Endpoint:** `POST /signup`
**Body (JSON):**

```json
{
  "username": "john",
  "password": "secret123"
}
```

---

### Step 2: Login and Get Tokens

**Endpoint:** `POST /login`
**Body (form-data/x-www-form-urlencoded):**

```
username=john
password=secret123
```

**Response:**

```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer"
}
```

---

### Step 3: Use Access Token in Requests

For all protected endpoints below, go to **Postman > Authorization tab**:

* Type: **Bearer Token**
* Token: Paste the `access_token` here

---

## 🧾 CRUD Operations (All Require Access Token)

### 🟩 Create Item

**POST /items/**
**Body:**

```json
{
  "name": "Book",
  "description": "A nice book"
}
```

---

### 🟨 Read Item

**GET /items/{item\_id}**

---

### 🟦 Update Item

**PUT /items/{item\_id}**
**Body:**

```json
{
  "name": "Updated Book",
  "description": "Updated description"
}
```

---

### 🟥 Delete Item

**DELETE /items/{item\_id}**

---

## 🔄 Refresh Token

When your access token expires:

**POST /refresh**
**Body (JSON):**

```json
{
  "refresh_token": "<refresh_token>"
}
```

**Response:**

```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<new_refresh_token>",
  "token_type": "bearer"
}
```

Use the new access token for future requests.

---

## 🧠 Summary of Key Concepts

| Concept             | Description                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| **Access Token**    | Used for accessing protected routes, short-lived                       |
| **Refresh Token**   | Used to generate a new access token, long-lived                        |
| **JWT**             | JSON Web Token for stateless authentication                            |
| **CRUD**            | Create, Read, Update, Delete operations for managing items             |
| **Postman Testing** | Use `/signup`, `/login`, then pass the `access_token` for item actions |

---

## 🛡️ Security Notes

* This code uses **in-memory fake databases** (`fake_users_db`, `fake_data_store`).
* Do **not** use in production; replace with real databases and HTTPS.

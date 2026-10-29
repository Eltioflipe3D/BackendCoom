# API Documentation

## Authentication
Most endpoints require a Bearer token in the Authorization header (format: `Bearer <token>`).

## Endpoints

### POST /register
Register a new user.

**Request Body:**
```json
{
  "username": "string (3-20 characters)",
  "email": "valid email",
  "password": "string (12-64 characters)"
}
```

**Response:**
```json
{"message": "user created"}
```
or
```json
{"message": "user already exists"}
```

### POST /login
Login and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{"token": "jwt_token_string"}
```
or
```json
{"token": null}
```

### GET /me
Get current user information.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "username": "string",
  "email": "string"
}
```

### POST /pfp
Upload or update profile picture.

**Headers:** Authorization: Bearer <token>

**Request:** Form data with file upload

**Response:**
```json
{"message": "profile picture updated"}
```

### GET /pfp/{username}
Get a user's profile picture.

**Path Parameter:** username

**Response:** Image file or
```json
{"message": "user not found"}
```

### PATCH /me/updatefield
Update a single field in user profile.

**Headers:** Authorization: Bearer <token>

**Query Parameters:**
- fieldName: string
- fieldValue: string

**Response:**
```json
{"message": true}
```

### GET /rankings/{num_rankings}
Get top rankings by best time.

**Path Parameter:** num_rankings (integer)

**Response:**
```json
[
  {
    "username": "string",
    "bestTime": integer,
    "difficulty": "string"
  }
]
```

### POST /rankings
Submit a new ranking.

**Headers:** Authorization: Bearer <token>

**Query Parameters:**
- time: integer (seconds)
- difficulty: string

**Response:**
```json
{"message": true}
```

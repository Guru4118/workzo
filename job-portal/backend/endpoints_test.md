# Job Portal API - Endpoint Testing Guide

Base URL: `http://localhost:8000`

---

## 1. Health Check Endpoints (No Auth Required)

### 1.1 Root Endpoint
```bash
curl -X GET http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "Welcome to Job Portal API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health",
  "ready": "/ready"
}
```

---

### 1.2 Health Check
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

---

### 1.3 Readiness Check
```bash
curl -X GET http://localhost:8000/ready
```

**Expected Response:**
```json
{
  "status": "ready",
  "database": "connected",
  "storage": null
}
```

---

## 2. Authentication Endpoints

### 2.1 Register New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "...",
  "email": "testuser@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "role": "viewer",
  "is_active": true,
  "created_at": "2024-...",
  "last_login": null
}
```

**Error Cases:**
- 400: Email already registered
- 400: Username already taken
- 422: Password validation failed (needs uppercase, lowercase, digit, min 8 chars)

---

### 2.2 Register Admin User (for testing)
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "AdminPass123",
    "full_name": "Admin User"
  }'
```

> **Note:** To make this user an admin, manually update in MongoDB:
> ```javascript
> db.users.updateOne({username: "admin"}, {$set: {role: "admin"}})
> ```

---

### 2.3 Login (Get Tokens)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=TestPass123"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

> **Save the access_token for subsequent requests:**
> ```bash
> export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
> ```

**Error Cases:**
- 401: Incorrect username/email or password
- 403: User account is disabled

---

### 2.4 Login with Email
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=TestPass123"
```

---

### 2.5 Refresh Token
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN_HERE"
  }'
```

**Expected Response:**
```json
{
  "access_token": "NEW_ACCESS_TOKEN...",
  "refresh_token": "NEW_REFRESH_TOKEN...",
  "token_type": "bearer"
}
```

**Error Cases:**
- 401: Invalid or expired refresh token

---

### 2.6 Get Current User Profile
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": "...",
  "email": "testuser@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "role": "viewer",
  "is_active": true,
  "created_at": "2024-...",
  "last_login": "2024-..."
}
```

**Error Cases:**
- 401: Could not validate credentials (missing/invalid token)

---

### 2.7 Change Password
```bash
curl -X POST http://localhost:8000/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "TestPass123",
    "new_password": "NewTestPass456"
  }'
```

**Expected Response:**
```json
{
  "message": "Password changed successfully"
}
```

**Error Cases:**
- 400: Current password is incorrect
- 400: New password must be different from current password
- 422: New password validation failed

---

## 3. Job Ingestion Endpoints (No Auth - For Scrapers)

### 3.1 Ingest Single Job
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company": "TechCorp Inc",
    "location": "Bangalore, India",
    "description": "We are looking for a senior Python developer...",
    "apply_url": "https://techcorp.com/jobs/123",
    "posted_date": "2024-11-20",
    "salary": "25,00,000 - 35,00,000",
    "source": "indeed"
  }'
```

**Expected Response (201 Created):**
```json
{
  "message": "Job received successfully",
  "data": {
    "dedupe_hash": "abc123..."
  }
}
```

**Error Cases:**
- 409: Job already exists (duplicate detected)
- 422: Validation error (missing title or company)
- 500: Database insert failed

---

### 3.2 Ingest Multiple Jobs (Batch)
```bash
curl -X POST http://localhost:8000/ingest/batch \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "title": "Frontend Developer",
        "company": "WebStudio",
        "location": "Mumbai, India",
        "source": "linkedin"
      },
      {
        "title": "Backend Engineer",
        "company": "DataSystems",
        "location": "Chennai, India",
        "source": "naukri"
      },
      {
        "title": "DevOps Engineer",
        "company": "CloudOps",
        "location": "Hyderabad, India",
        "salary": "20L - 30L",
        "source": "indeed"
      }
    ]
  }'
```

**Expected Response (201 Created):**
```json
{
  "message": "Batch processing complete: 3 inserted, 0 duplicates, 0 errors",
  "data": {
    "inserted": 3,
    "duplicates": 0,
    "errors": 0
  }
}
```

---

### 3.3 Test Duplicate Detection
```bash
# Run the same request again - should be detected as duplicate
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company": "TechCorp Inc",
    "location": "Bangalore, India",
    "posted_date": "2024-11-20",
    "source": "indeed"
  }'
```

**Expected Response (409 Conflict):**
```json
{
  "detail": "Job already exists (duplicate detected by dedupe_hash)"
}
```

---

## 4. Public Jobs Endpoints (No Auth Required)

### 4.1 List All Approved Jobs
```bash
curl -X GET "http://localhost:8000/jobs"
```

**Expected Response:**
```json
{
  "page": 1,
  "per_page": 20,
  "total": 0,
  "total_pages": 1,
  "data": []
}
```

> Note: Initially empty until jobs are approved by admin

---

### 4.2 List Jobs with Pagination
```bash
curl -X GET "http://localhost:8000/jobs?page=1&per_page=10"
```

---

### 4.3 Search Jobs
```bash
curl -X GET "http://localhost:8000/jobs?q=python"
```

---

### 4.4 Filter Jobs by Source
```bash
curl -X GET "http://localhost:8000/jobs?source=indeed"
```

---

### 4.5 Filter Jobs by Location
```bash
curl -X GET "http://localhost:8000/jobs?location=bangalore"
```

---

### 4.6 Combined Filters
```bash
curl -X GET "http://localhost:8000/jobs?q=developer&source=linkedin&location=mumbai&page=1&per_page=10"
```

---

### 4.7 Get Single Job by ID
```bash
curl -X GET "http://localhost:8000/jobs/JOB_ID_HERE"
```

**Expected Response:**
```json
{
  "id": "...",
  "title": "Senior Python Developer",
  "company": "TechCorp Inc",
  "location": "Bangalore, India",
  "description": "...",
  "apply_url": "...",
  "posted_date": "2024-11-20",
  "posted_date_parsed": "2024-11-20",
  "salary": "25,00,000 - 35,00,000",
  "salary_parsed": {"min": 2500000, "max": 3500000},
  "location_normalized": {"raw": "Bangalore, India", "lat": 12.97, "lon": 77.59, "display_name": "..."},
  "tags": ["seniority:senior", "skill:python", "source:indeed"],
  "source": "indeed",
  "approved_at": "2024-..."
}
```

**Error Cases:**
- 400: Invalid job ID format
- 404: Job not found

---

### 4.8 Get Jobs by Source
```bash
curl -X GET "http://localhost:8000/jobs/source/indeed?page=1&per_page=20"
```

---

## 5. Admin Endpoints (Auth Required)

> **Important:** For admin endpoints, you need to:
> 1. Login to get a token
> 2. Use the token in Authorization header
> 3. Some endpoints require "admin" role (not just "viewer")

### 5.1 Get Pending Jobs (viewer or admin)
```bash
curl -X GET "http://localhost:8000/admin/pending" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "page": 1,
  "per_page": 20,
  "total": 4,
  "total_pages": 1,
  "data": [
    {
      "id": "674b...",
      "title": "Senior Python Developer",
      "company": "TechCorp Inc",
      "location": "Bangalore, India",
      "dedupe_hash": "...",
      "posted_date_parsed": "2024-11-20",
      "salary_parsed": {"min": 2500000, "max": 3500000},
      "location_normalized": {...},
      "tags": ["seniority:senior", "skill:python", "source:indeed"],
      "ingested_at": "2024-11-25T..."
    },
    ...
  ]
}
```

**Error Cases:**
- 401: Not authenticated
- 403: Insufficient permissions

---

### 5.2 Search Pending Jobs
```bash
curl -X GET "http://localhost:8000/admin/pending?q=python&page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5.3 Filter Pending Jobs by Source
```bash
curl -X GET "http://localhost:8000/admin/pending?source=indeed" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5.4 Approve a Job (admin only)
```bash
curl -X POST http://localhost:8000/admin/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_ID_FROM_PENDING_LIST"
  }'
```

**Expected Response:**
```json
{
  "message": "Job approved successfully",
  "data": null
}
```

**Error Cases:**
- 400: Invalid job ID format
- 401: Not authenticated
- 403: Insufficient permissions (requires admin)
- 404: Job not found in pending queue

---

### 5.5 Reject a Job (admin only)
```bash
curl -X POST http://localhost:8000/admin/reject \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_ID_FROM_PENDING_LIST",
    "reason": "Duplicate job posting"
  }'
```

**Expected Response:**
```json
{
  "message": "Job rejected successfully",
  "data": null
}
```

---

### 5.6 Bulk Approve Jobs (admin only)
```bash
curl -X POST http://localhost:8000/admin/bulk-approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": [
      "JOB_ID_1",
      "JOB_ID_2",
      "JOB_ID_3"
    ]
  }'
```

**Expected Response:**
```json
{
  "message": "Bulk approval complete: 3 approved, 0 not found, 0 errors",
  "data": {
    "success": 3,
    "not_found": 0,
    "errors": 0
  }
}
```

---

### 5.7 Bulk Reject Jobs (admin only)
```bash
curl -X POST http://localhost:8000/admin/bulk-reject \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": [
      "JOB_ID_1",
      "JOB_ID_2"
    ],
    "reason": "Low quality job postings"
  }'
```

**Expected Response:**
```json
{
  "message": "Bulk rejection complete: 2 rejected, 0 not found, 0 errors",
  "data": {
    "success": 2,
    "not_found": 0,
    "errors": 0
  }
}
```

---

### 5.8 Get Job Statistics (viewer or admin)
```bash
curl -X GET http://localhost:8000/admin/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "total_raw": 10,
  "total_pending": 5,
  "total_approved": 3,
  "total_rejected": 2,
  "jobs_by_source": {
    "indeed": 4,
    "linkedin": 3,
    "naukri": 2,
    "unknown": 1
  },
  "jobs_today": 4,
  "jobs_this_week": 10
}
```

---

### 5.9 Get Rejected Jobs (viewer or admin)
```bash
curl -X GET "http://localhost:8000/admin/rejected?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "page": 1,
  "per_page": 20,
  "total": 2,
  "total_pages": 1,
  "data": [
    {
      "id": "...",
      "title": "...",
      "company": "...",
      "rejected_at": "2024-11-25T...",
      "rejected_by": "admin",
      "rejection_reason": "Duplicate job posting"
    }
  ]
}
```

---

### 5.10 Search Rejected Jobs
```bash
curl -X GET "http://localhost:8000/admin/rejected?q=developer" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. Error Response Formats

### 6.1 Validation Error (422)
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```

### 6.2 Authentication Error (401)
```json
{
  "detail": "Could not validate credentials"
}
```

### 6.3 Authorization Error (403)
```json
{
  "detail": "Insufficient permissions. Required role: admin"
}
```

### 6.4 Not Found (404)
```json
{
  "detail": "Job not found"
}
```

### 6.5 Conflict (409)
```json
{
  "detail": "Job already exists (duplicate detected by dedupe_hash)"
}
```

### 6.6 Internal Server Error (500)
```json
{
  "detail": "Internal server error"
}
```

---

## 7. Complete Test Script (PowerShell)

```powershell
# Base URL
$BASE_URL = "http://localhost:8000"

# Test Health Endpoints
Write-Host "=== Testing Health Endpoints ===" -ForegroundColor Green
Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
Invoke-RestMethod -Uri "$BASE_URL/ready" -Method Get

# Register User
Write-Host "`n=== Registering User ===" -ForegroundColor Green
$registerBody = @{
    email = "test$(Get-Random)@example.com"
    username = "testuser$(Get-Random)"
    password = "TestPass123"
    full_name = "Test User"
} | ConvertTo-Json

$user = Invoke-RestMethod -Uri "$BASE_URL/auth/register" -Method Post -Body $registerBody -ContentType "application/json"
Write-Host "Registered user: $($user.username)"

# Login
Write-Host "`n=== Logging In ===" -ForegroundColor Green
$loginBody = "username=$($user.username)&password=TestPass123"
$tokens = Invoke-RestMethod -Uri "$BASE_URL/auth/login" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
$token = $tokens.access_token
Write-Host "Got access token"

# Get Profile
Write-Host "`n=== Getting Profile ===" -ForegroundColor Green
$headers = @{ Authorization = "Bearer $token" }
$profile = Invoke-RestMethod -Uri "$BASE_URL/auth/me" -Method Get -Headers $headers
Write-Host "Profile: $($profile.email) - Role: $($profile.role)"

# Ingest Job
Write-Host "`n=== Ingesting Job ===" -ForegroundColor Green
$jobBody = @{
    title = "Test Developer $(Get-Random)"
    company = "Test Company"
    location = "Bangalore, India"
    source = "test"
} | ConvertTo-Json

$ingestResult = Invoke-RestMethod -Uri "$BASE_URL/ingest" -Method Post -Body $jobBody -ContentType "application/json"
Write-Host "Ingested job: $($ingestResult.message)"

# Get Pending Jobs
Write-Host "`n=== Getting Pending Jobs ===" -ForegroundColor Green
$pending = Invoke-RestMethod -Uri "$BASE_URL/admin/pending" -Method Get -Headers $headers
Write-Host "Pending jobs: $($pending.total)"

# Get Stats
Write-Host "`n=== Getting Stats ===" -ForegroundColor Green
$stats = Invoke-RestMethod -Uri "$BASE_URL/admin/stats" -Method Get -Headers $headers
Write-Host "Total Raw: $($stats.total_raw), Pending: $($stats.total_pending), Approved: $($stats.total_approved)"

# Get Public Jobs
Write-Host "`n=== Getting Public Jobs ===" -ForegroundColor Green
$jobs = Invoke-RestMethod -Uri "$BASE_URL/jobs" -Method Get
Write-Host "Approved jobs: $($jobs.total)"

Write-Host "`n=== All Tests Complete ===" -ForegroundColor Green
```

---

## 8. Complete Test Script (Bash/Linux/Mac)

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
RANDOM_ID=$RANDOM

echo "=== Testing Health Endpoints ==="
curl -s "$BASE_URL/" | jq .
curl -s "$BASE_URL/health" | jq .
curl -s "$BASE_URL/ready" | jq .

echo -e "\n=== Registering User ==="
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test${RANDOM_ID}@example.com\",
    \"username\": \"testuser${RANDOM_ID}\",
    \"password\": \"TestPass123\",
    \"full_name\": \"Test User\"
  }")
echo $REGISTER_RESPONSE | jq .
USERNAME=$(echo $REGISTER_RESPONSE | jq -r '.username')

echo -e "\n=== Logging In ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=TestPass123")
echo $LOGIN_RESPONSE | jq .
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

echo -e "\n=== Getting Profile ==="
curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n=== Ingesting Job ==="
curl -s -X POST "$BASE_URL/ingest" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Developer ${RANDOM_ID}\",
    \"company\": \"Test Company\",
    \"location\": \"Bangalore, India\",
    \"source\": \"test\"
  }" | jq .

echo -e "\n=== Getting Pending Jobs ==="
curl -s -X GET "$BASE_URL/admin/pending" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n=== Getting Stats ==="
curl -s -X GET "$BASE_URL/admin/stats" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n=== Getting Public Jobs ==="
curl -s -X GET "$BASE_URL/jobs" | jq .

echo -e "\n=== All Tests Complete ==="
```

---

## 9. Testing with HTTPie (Alternative to curl)

```bash
# Install: pip install httpie

# Health
http GET localhost:8000/health

# Register
http POST localhost:8000/auth/register email=test@example.com username=testuser password=TestPass123

# Login
http --form POST localhost:8000/auth/login username=testuser password=TestPass123

# Authenticated requests
http GET localhost:8000/auth/me "Authorization: Bearer YOUR_TOKEN"

# Ingest job
http POST localhost:8000/ingest title="Python Dev" company="TechCorp" location="Bangalore"
```

---

## 10. Quick Reference Card

| Endpoint | Method | Auth | Role | Description |
|----------|--------|------|------|-------------|
| `/` | GET | No | - | Welcome |
| `/health` | GET | No | - | Health check |
| `/ready` | GET | No | - | Readiness check |
| `/auth/register` | POST | No | - | Register user |
| `/auth/login` | POST | No | - | Get tokens |
| `/auth/refresh` | POST | No | - | Refresh token |
| `/auth/me` | GET | Yes | Any | User profile |
| `/auth/change-password` | POST | Yes | Any | Change password |
| `/ingest` | POST | No | - | Ingest job |
| `/ingest/batch` | POST | No | - | Batch ingest |
| `/jobs` | GET | No | - | List approved |
| `/jobs/{id}` | GET | No | - | Job detail |
| `/jobs/source/{source}` | GET | No | - | Jobs by source |
| `/admin/pending` | GET | Yes | viewer+ | Pending jobs |
| `/admin/approve` | POST | Yes | admin | Approve job |
| `/admin/reject` | POST | Yes | admin | Reject job |
| `/admin/bulk-approve` | POST | Yes | admin | Bulk approve |
| `/admin/bulk-reject` | POST | Yes | admin | Bulk reject |
| `/admin/stats` | GET | Yes | viewer+ | Statistics |
| `/admin/rejected` | GET | Yes | viewer+ | Rejected jobs |

---

## Notes

1. **Token Expiry**: Access tokens expire in 30 minutes by default. Use refresh token to get new tokens.

2. **Admin Role**: To test admin endpoints, you need to manually update a user's role to "admin" in MongoDB:
   ```javascript
   db.users.updateOne({username: "yourusername"}, {$set: {role: "admin"}})
   ```

3. **API Documentation**: When running in debug mode, interactive docs are available at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

4. **Rate Limiting**: API has rate limiting enabled. If you get 429 errors, wait and retry.

5. **CORS**: By default, only `http://localhost:3000` is allowed. Update `ALLOWED_ORIGINS` in `.env` for other origins.

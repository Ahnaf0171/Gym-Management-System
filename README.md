# Gym Management & Member Workout System API

A comprehensive backend REST API for managing multiple gym branches, trainers, members, and workout assignments built with Django and Django REST Framework.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Test Users](#test-users)
- [API Endpoints](#api-endpoints)
- [User Roles & Permissions](#user-roles--permissions)

## 🎯 Overview

This system allows fitness companies to manage multiple gym branches with different user roles, create workout plans, and assign workout tasks to members. The API enforces strict branch isolation and role-based access control.

## ✨ Features

- **Multi-Branch Management**: Handle multiple gym locations
- **Role-Based Access Control**: 4 distinct user roles (Super Admin, Manager, Trainer, Member)
- **JWT Authentication**: Secure token-based authentication
- **Workout Management**: Create plans and assign tasks
- **Branch Isolation**: Users can only access data from their branch
- **Optimized Queries**: Performance-optimized database queries

## 🛠 Technology Stack

- **Backend**: Django 4.2+
- **API**: Django REST Framework 3.14+
- **Authentication**: Simple JWT
- **Database**: SQLite
- **Python**: 3.10+

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gym_management
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Test Data

```bash
python manage.py create_test_users
```

### 6. Start Server

```bash
python manage.py runserver
```

API will run at: `http://127.0.0.1:8000/`

## 👥 Test Users

### Super Admin

```json
{
  "email": "admin@gmail.com",
  "password": "12345"
}
```

**Can do**: Create branches, add managers, view all data

### Manager (Branch 2)

```json
{
  "email": "manager2@gmail.com",
  "password": "Manager@1234"
}
```

**Can do**: Create trainers/members, view branch data

### Trainer

```json
{
  "email": "trainer_jabed@gmail.com",
  "password": "Trainer@1234"
}
```

**Can do**: Create workout plans, assign tasks

### Member

```json
{
  "email": "member_nahin@gmail.com",
  "password": "Member@1234"
}
```

**Can do**: View and update own tasks

## 📡 API Endpoints

### 🔐 Authentication

#### 1. Login

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "admin@gmail.com",
  "password": "12345"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@gmail.com",
    "role": "super_admin"
  }
}
```

#### 2. Refresh Token

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "{{refresh_token}}"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 3. Get Current User Profile

```http
GET /api/v1/auth/users/me/
Authorization: Bearer {{access_token}}

Response:
{
  "id": 1,
  "email": "admin@gmail.com",
  "role": "super_admin",
  "gym_branch": null
}
```

#### 4. List Users (Manager/Admin Only)

```http
GET /api/v1/auth/users/
Authorization: Bearer {{access_token}}
```

#### 5. Create User (Admin creates Manager, Manager creates Trainer/Member)

```http
POST /api/v1/auth/users/
Authorization: Bearer {{access_token}}
Content-Type: application/json

# Admin creates Manager:
{
  "email": "manager_tania@gmail.com",
  "password": "Manager@9012",
  "role": "gym_manager",
  "gym_branch": 3
}

# Manager creates Trainer:
{
  "email": "trainer_sakibal_hasan@gmail.com",
  "password": "Trainer@9012",
  "role": "trainer"
}

# Manager creates Member:
{
  "email": "member_rafia@gmail.com",
  "password": "Member@9012",
  "role": "member"
}
```

### 🏢 Gym Branches

#### 1. List All Branches

```http
GET /api/v1/branches/
Authorization: Bearer {{access_token}}
```

#### 2. Create Branch (Super Admin Only)

```http
POST /api/v1/branches/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "name": "Uttara North Branch",
  "location": "Uttara Sector-14, Dhaka"
}

Response:
{
  "id": 3,
  "name": "Uttara North Branch",
  "location": "Uttara Sector-14, Dhaka",
  "created_at": "2026-01-15T10:00:00Z"
}
```

### 💪 Workout Plans

#### 1. List Workout Plans (Trainer/Manager)

```http
GET /api/v1/workout-plans/
Authorization: Bearer {{access_token}}

Response:
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "Strength Builder - Week 1",
      "description": "Compound lifts + light cardio",
      "created_by_email": "trainer_jabed@gmail.com",
      "gym_branch_name": "Downtown Branch"
    }
  ]
}
```

#### 2. Create Workout Plan (Trainer Only)

```http
POST /api/v1/workout-plans/
Authorization: Bearer {{trainer_access_token}}
Content-Type: application/json

{
  "title": "Strength Builder - Week 1",
  "description": "Compound lifts + light cardio (4 sessions).",
  "gym_branch": 1
}

Response:
{
  "id": 1,
  "title": "Strength Builder - Week 1",
  "description": "Compound lifts + light cardio (4 sessions).",
  "created_by": 3,
  "created_by_email": "trainer_jabed@gmail.com",
  "gym_branch": 1,
  "gym_branch_name": "Downtown Branch",
  "created_at": "2026-01-15T13:00:00Z"
}
```

### ✅ Workout Tasks

#### 1. List Tasks

```http
GET /api/v1/workout-tasks/
Authorization: Bearer {{access_token}}

# Trainer/Manager: sees all branch tasks
# Member: sees only own tasks

Response:
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "workout_plan": 1,
      "workout_plan_title": "Strength Builder - Week 1",
      "member": 7,
      "member_email": "member_nahin@gmail.com",
      "status": "pending",
      "due_date": "2026-02-10"
    }
  ]
}
```

#### 2. Create Task (Trainer Only)

```http
POST /api/v1/workout-tasks/
Authorization: Bearer {{trainer_access_token}}
Content-Type: application/json

{
  "workout_plan": 1,
  "member": 7,
  "due_date": "2026-02-10"
}

Response:
{
  "id": 1,
  "workout_plan": 1,
  "workout_plan_title": "Strength Builder - Week 1",
  "member": 7,
  "member_email": "member_nahin@gmail.com",
  "status": "pending",
  "due_date": "2026-02-10",
  "created_at": "2026-01-15T14:00:00Z"
}
```

#### 3. Update Task Status (Trainer/Member)

```http
PATCH /api/v1/workout-tasks/1/
Authorization: Bearer {{access_token}}
Content-Type: application/json

# Trainer updates:
{
  "status": "in_progress"
}

# Member updates (own task only):
{
  "status": "completed"
}

Response:
{
  "id": 1,
  "status": "completed",
  "workout_plan_title": "Strength Builder - Week 1",
  "member_email": "member_nahin@gmail.com"
}
```

#### 4. Full Update Task (Trainer Only)

```http
PUT /api/v1/workout-tasks/1/
Authorization: Bearer {{trainer_access_token}}
Content-Type: application/json

{
  "workout_plan": 1,
  "member": 7,
  "status": "in_progress",
  "due_date": "2026-02-15"
}
```

## 📊 Complete API Reference

### Authentication

| Method | Endpoint                      | Access        | Description          |
| ------ | ----------------------------- | ------------- | -------------------- |
| POST   | `/api/v1/auth/login/`         | Public        | Login and get tokens |
| POST   | `/api/v1/auth/token/refresh/` | Public        | Refresh access token |
| GET    | `/api/v1/auth/users/me/`      | Authenticated | Get current user     |
| GET    | `/api/v1/auth/users/`         | Admin/Manager | List users           |
| POST   | `/api/v1/auth/users/`         | Admin/Manager | Create user          |

### Branches

| Method | Endpoint            | Access | Description       |
| ------ | ------------------- | ------ | ----------------- |
| GET    | `/api/v1/branches/` | Admin  | List all branches |
| POST   | `/api/v1/branches/` | Admin  | Create branch     |

### Workout Plans

| Method | Endpoint                 | Access          | Description |
| ------ | ------------------------ | --------------- | ----------- |
| GET    | `/api/v1/workout-plans/` | Trainer/Manager | List plans  |
| POST   | `/api/v1/workout-plans/` | Trainer         | Create plan |

### Workout Tasks

| Method | Endpoint                      | Access                 | Description |
| ------ | ----------------------------- | ---------------------- | ----------- |
| GET    | `/api/v1/workout-tasks/`      | Trainer/Manager/Member | List tasks  |
| POST   | `/api/v1/workout-tasks/`      | Trainer                | Create task |
| PATCH  | `/api/v1/workout-tasks/{id}/` | Trainer/Member         | Update task |
| PUT    | `/api/v1/workout-tasks/{id}/` | Trainer                | Full update |

## 🎭 User Roles & Permissions

### Super Admin

✅ Create gym branches  
✅ Add gym managers  
✅ View all data across branches  
✅ Bypass branch restrictions  
❌ Cannot create workout plans/tasks directly

### Gym Manager

✅ Create trainers (max 3 per branch)  
✅ Create members for their branch  
✅ View all members and workouts in branch  
❌ Cannot access other branches  
❌ Cannot create workout plans/tasks

### Trainer

✅ Create workout plans  
✅ Assign tasks to members  
✅ Update task status  
✅ View branch members  
❌ Cannot assign tasks across branches  
❌ Cannot create/modify users

### Member

✅ View own assigned tasks  
✅ Update own task status  
❌ Cannot view other members' tasks  
❌ Cannot view workout plans directly  
❌ Cannot modify assignments

## 🔒 Business Rules

1. **Branch Isolation**: Users can only access their branch data (except Super Admin)
2. **Trainer Limit**: Maximum 3 trainers per gym branch
3. **Task Assignment**: Trainers can only assign tasks within their branch
4. **Task Ownership**: Members can only update their own tasks
5. **No Reassignment**: Cannot change member/plan after task creation
6. **User Creation**: Managers create users only for their branch
7. **Role Validation**: Plans created by Trainers, Tasks assigned to Members

## 🧪 Testing the API

### Using Postman/Thunder Client:

1. **Login** with any test user
2. **Copy** the `access` token from response
3. **Add** Authorization header: `Bearer {access_token}`
4. **Test** endpoints based on user role

### Example Flow:

```
1. Login as Admin → Create Branch
2. Login as Admin → Create Manager for that Branch
3. Login as Manager → Create Trainer
4. Login as Manager → Create Member
5. Login as Trainer → Create Workout Plan
6. Login as Trainer → Assign Task to Member
7. Login as Member → View and Update Task
```

## 📦 Project Structure

```
gym_management/
├── accounts/           # User & authentication
├── gym_branches/       # Branch management
├── workouts/           # Plans & tasks
├── db.sqlite3          # SQLite database
├── manage.py
└── requirements.txt
``
```

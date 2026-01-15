# Gym Management & Member Workout System API

A comprehensive backend REST API for managing multiple gym branches, trainers, members, and workout assignments built with Django and Django REST Framework.

**Live API**: `https://gym-management-system-otli.onrender.com`

## Features

- **Multi-Branch Management**: Handle multiple gym locations with strict branch isolation
- **Role-Based Access Control**: 4 distinct user roles (Super Admin, Manager, Trainer, Member)
- **JWT Authentication**: Secure token-based authentication
- **Workout Management**: Create workout plans and assign tasks to members
- **Optimized Performance**: Performance-optimized database queries

## 🛠 Technology Stack

- Django 4.2+ & Django REST Framework 3.14+
- Simple JWT Authentication
- SQLite Database
- Python 3.10+

## Test Users

### Super Admin

```json
{
  "email": "admin@gmail.com",
  "password": "12345"
}
```

### Manager (Branch 2)

```json
{
  "email": "manager2@gmail.com",
  "password": "Manager@1234"
}
```

### Trainer

```json
{
  "email": "trainer_jabed@gmail.com",
  "password": "Trainer@1234"
}
```

### Member

```json
{
  "email": "member_nahin@gmail.com",
  "password": "Member@1234"
}
```

## 📡 API Endpoints

### Authentication

**Login**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/auth/login/
Content-Type: application/json

{
  "email": "admin@gmail.com",
  "password": "12345"
}
```

**Refresh Token**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "{{refresh_token}}"
}
```

**Get Current User**

```http
GET https://gym-management-system-otli.onrender.com/api/v1/auth/users/me/
Authorization: Bearer {{access_token}}
```

**Create User**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/auth/users/
Authorization: Bearer {{access_token}}

# Admin creates Manager:
{
  "email": "manager@example.com",
  "password": "Manager@1234",
  "role": "gym_manager",
  "gym_branch": 3
}

# Manager creates Trainer/Member:
{
  "email": "trainer@example.com",
  "password": "Trainer@1234",
  "role": "trainer"
}
```

### Gym Branches

**List Branches**

```http
GET https://gym-management-system-otli.onrender.com/api/v1/branches/
Authorization: Bearer {{access_token}}
```

**Create Branch (Super Admin Only)**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/branches/
Authorization: Bearer {{access_token}}

{
  "name": "Uttara North Branch",
  "location": "Uttara Sector-14, Dhaka"
}
```

### Workout Plans

**List Plans**

```http
GET https://gym-management-system-otli.onrender.com/api/v1/workout-plans/
Authorization: Bearer {{access_token}}
```

**Create Plan (Trainer Only)**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/workout-plans/
Authorization: Bearer {{trainer_access_token}}

{
  "title": "Strength Builder - Week 1",
  "description": "Compound lifts + light cardio",
  "gym_branch": 1
}
```

### Workout Tasks

**List Tasks**

```http
GET https://gym-management-system-otli.onrender.com/api/v1/workout-tasks/
Authorization: Bearer {{access_token}}
```

**Create Task (Trainer Only)**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/workout-tasks/
Authorization: Bearer {{trainer_access_token}}

{
  "workout_plan": 1,
  "member": 7,
  "due_date": "2026-02-10"
}
```

**Update Task Status**

```http
PATCH https://gym-management-system-otli.onrender.com/api/v1/workout-tasks/1/
Authorization: Bearer {{access_token}}

{
  "status": "completed"
}
```

## API Reference Summary

| Endpoint                      | Method         | Access          | Description     |
| ----------------------------- | -------------- | --------------- | --------------- |
| `/api/v1/auth/login/`         | POST           | Public          | Login           |
| `/api/v1/auth/token/refresh/` | POST           | Public          | Refresh token   |
| `/api/v1/auth/users/me/`      | GET            | Authenticated   | Current user    |
| `/api/v1/auth/users/`         | GET/POST       | Admin/Manager   | Manage users    |
| `/api/v1/branches/`           | GET/POST       | Admin           | Manage branches |
| `/api/v1/workout-plans/`      | GET/POST       | Trainer/Manager | Manage plans    |
| `/api/v1/workout-tasks/`      | GET/POST/PATCH | All roles       | Manage tasks    |

## User Roles & Permissions

**Super Admin**: Create branches, add managers, view all data across branches

**Gym Manager**: Create trainers (max 3 per branch) and members, view branch data

**Trainer**: Create workout plans, assign tasks to members, update task status

**Member**: View and update own assigned tasks only

## Key Business Rules

- **Branch Isolation**: Users can only access their branch data (except Super Admin)
- **Trainer Limit**: Maximum 3 trainers per gym branch
- **Task Assignment**: Trainers assign tasks only within their branch
- **Task Ownership**: Members can only update their own tasks
- **Role Hierarchy**: Admin → Manager → Trainer → Member

## Quick Test Flow

1. Login as Admin → Create Branch
2. Login as Admin → Create Manager for Branch
3. Login as Manager → Create Trainer & Member
4. Login as Trainer → Create Workout Plan
5. Login as Trainer → Assign Task to Member
6. Login as Member → View and Update Task

## Local Setup

```bash
# Clone repository
git clone <repository-url>
cd gym_management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create test data
python manage.py create_test_users

# Start server
python manage.py runserver
```

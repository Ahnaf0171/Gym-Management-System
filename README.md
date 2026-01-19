# Gym Management System API

A backend REST API for managing multiple gym branches, trainers, members, and workout assignments built with Django and Django REST Framework.

**Live API**: `https://gym-management-system-otli.onrender.com`

**API Documentation (Swagger)**: `https://gym-management-system-otli.onrender.com/api/docs/`

## Features

- **Multi-Branch Management**: Handle multiple gym locations with strict branch isolation
- **Role-Based Access Control**: 4 distinct user roles (Super Admin, Manager, Trainer, Member)
- **JWT Authentication**: Secure token-based authentication
- **Workout Management**: Create workout plans and assign tasks to members
- **Optimized Performance**: Performance-optimized database queries

### Database Dump (Schema, Data and Overview)

- File: `database/db_dump.json`
- Contains sample data for all core entities (GymBranch, User, WorkoutPlan, WorkoutTask).
- Restore command:
  ```bash
  python manage.py loaddata database/db_dump.json
  ```

### Entities / Tables

- **GymBranch**: id, name, location, created_at, updated_at
- **User**: email (unique), role, gym_branch (nullable for super_admin), is_active, is_staff, created_at, updated_at
- **WorkoutPlan**: title, description, created_by (Trainer), gym_branch, created_at, updated_at
- **WorkoutTask**: workout_plan, member, status, due_date, created_at, updated_at

### Relationships

- GymBranch 1—N User
- GymBranch 1—N WorkoutPlan
- User(Trainer) 1—N WorkoutPlan (created_by)
- WorkoutPlan 1—N WorkoutTask
- User(Member) 1—N WorkoutTask (member)

## Test Users

### Super Admin

```json
{
  "email": "superadmin@gmail.com",
  "password": "Admin@1234"
}
```

### Manager (Dhanmondi Branch)

```json
{
  "email": "manager_rakib@gmail.com",
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

## API Endpoints

### Authentication

**Login**

```http
POST https://gym-management-system-otli.onrender.com/api/v1/auth/login/
Content-Type: application/json

{
  "email": "superadmin@gmail.com",
  "password": "Admin@1234"
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

# Seed database with test users
python manage.py seed

# Start server
python manage.py runserver
```

### Seed Command Details

The `seed` management command (`accounts/management/commands/seed.py`) creates test users and a default branch:

- **Super Admin**: `superadmin@gmail.com` (password: `Admin@1234`)
- **Manager**: `manager_rakib@gmail.com` (password: `Manager@1234`) for Dhanmondi Branch
- **Trainers**: 3 trainers (alif, jabed, rakib) with `Trainer@1234`
- **Member**: `member_nahin@gmail.com` with `Member@1234`
- **Branch**: Dhanmondi Branch, Dhaka

Run `python manage.py seed` to populate the database. The command is idempotent and respects the 3-trainer-per-branch limit.

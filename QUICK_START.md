# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

### Step 2: Start the Application

**Option A: Use Management Script (Easiest)**
```powershell
# From project root
.\manage-workflow-monitoring.ps1 start
```

**Option B: Manual Start**

Terminal 1 (Backend):
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```

### Step 3: Access the Application

- **Web Interface**: http://localhost:3009
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

## 📝 First Steps

### 1. Create Admin User

Visit http://localhost:8000/docs and use the `/api/v1/auth/register` endpoint:

```json
{
  "email": "admin@example.com",
  "username": "admin",
  "password": "Admin123!",
  "full_name": "Admin User",
  "role": "admin"
}
```

### 2. Login

Use `/api/v1/auth/login` endpoint or login via the web interface at http://localhost:3009

### 3. Test the API

- Click "Authorize" in Swagger UI
- Login first to get token
- Copy the `access_token` from response
- Paste as: `Bearer <your_token>`
- Now test all endpoints!

## 🧪 Testing Checklist

- [ ] Backend starts successfully
- [ ] Frontend starts successfully  
- [ ] Can register a user
- [ ] Can login and get token
- [ ] Can create a camera
- [ ] Can create a rule
- [ ] Can list events
- [ ] Can list alerts

## 📚 More Information

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed testing instructions.


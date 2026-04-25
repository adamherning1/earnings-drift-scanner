# 🚀 Step-by-Step Deployment Instructions

## Phase 1: Deploy V2 with Database & Auth (Do This First!)

### Step 1: Upload the new file
1. Go to: https://github.com/adamherning1/earnings-drift-scanner/tree/main/api
2. Click "Add file" → "Upload files"
3. Upload the `simple_main_v2.py` file
4. Commit message: "Add v2 with database and auth"
5. Click "Commit changes"

### Step 2: Update Render Settings
1. Go to your Render dashboard
2. Click on your earnings-scanner-api service
3. Go to Settings → Build & Deploy
4. Change Start Command to:
   ```
   uvicorn simple_main_v2:app --host 0.0.0.0 --port $PORT
   ```
5. Click "Save Changes"

### Step 3: Watch the deployment
- Render will automatically rebuild
- Check logs for any errors
- Should take 2-3 minutes

### Step 4: Test the new endpoints
Once deployed, test these:

1. **Check root**: https://earnings-scanner-api.onrender.com/
   - Should show v2.0 info

2. **Check docs**: https://earnings-scanner-api.onrender.com/docs
   - Should show all new endpoints

3. **Register a test user** (use Postman or the /docs interface):
   ```
   POST /register
   {
     "email": "test@example.com",
     "username": "testuser",
     "password": "testpass123"
   }
   ```

4. **Login** (will return a JWT token):
   ```
   POST /token
   Form data:
   - username: testuser (or email)
   - password: testpass123
   ```

5. **Test protected route** (add the token to Authorization header):
   ```
   GET /users/me
   Authorization: Bearer <your-token-here>
   ```

## Phase 2: Add Missing Dependencies (After V2 Works)

If V2 deploys successfully, gradually add these to requirements.txt:

### Add Market Data Support:
```
yfinance==0.2.38
```

### Add Data Processing (try one at a time):
```
pandas==2.1.4
numpy==1.24.3
```

### Add Payment Processing:
```
stripe==9.4.0
```

### Add Email Support:
```
sendgrid==6.11.0
```

## Phase 3: Migrate Full App (Once Dependencies Work)

1. Rename `simple_main_v2.py` to `main.py`
2. Delete the old `app/main.py`
3. Update start command to:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

## 🚨 Troubleshooting

**If deployment fails:**
1. Check logs for the specific error
2. Remove the last change
3. Try again

**Common issues:**
- Missing import → Add to requirements.txt
- Database error → Check DATABASE_URL env var
- Auth error → Check SECRET_KEY env var

## 📝 Testing Checklist

After deployment, verify:
- [ ] API root endpoint works
- [ ] /docs page loads
- [ ] Can register new user
- [ ] Can login and get token
- [ ] Protected routes require token
- [ ] Database persists data

## 🎯 Success Criteria

You'll know it's working when:
1. All endpoints respond without errors
2. User registration creates database entries
3. Login returns valid JWT tokens
4. Protected routes block unauthorized access
5. The API stays up without crashing

---

Remember: **Test after each change!** Don't add multiple features at once.
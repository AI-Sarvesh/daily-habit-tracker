# Pre-Deployment Checklist ✅

## Before Pushing to GitHub

- [x] `.gitignore` created (protects `.env` and `data/`)
- [x] `.env.example` created (template for others)
- [x] `.streamlit/config.toml` created (fixes Render deployment issue)
- [x] `Procfile` created (tells Render how to run the app)
- [x] `requirements.txt` updated (python-dotenv added)
- [x] `README.md` exists
- [x] `DEPLOYMENT.md` created (deployment guide)

## Git Commands to Push

```bash
# If not already initialized
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Daily Habit Tracker with multi-user support"

# Create GitHub repo first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Render Setup

### Build Command:
```
pip install -r requirements.txt
```

### Start Command:
```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### Environment Variables to Set:
Copy from your `.env` file - **DO NOT UPLOAD .env TO GITHUB!**

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
USER_1_USERNAME=john
USER_1_PASSWORD=john123
USER_1_DISPLAYNAME=John 🏃
USER_2_USERNAME=sarah
USER_2_PASSWORD=sarah123
USER_2_DISPLAYNAME=Sarah 💪
USER_3_USERNAME=mike
USER_3_PASSWORD=mike123
USER_3_DISPLAYNAME=Mike 🎯
```

## Post-Deployment

- [ ] Test login with all users
- [ ] Create some test habits
- [ ] Verify leaderboard updates
- [ ] Share URL with friends
- [ ] Add friends' credentials to Render environment variables

## Notes

⚠️ **Important:** 
- Never commit `.env` to GitHub (already in `.gitignore`)
- Render free tier: database resets on redeploy
- App sleeps after 15 min inactivity
- First wake-up takes ~30 seconds

🎉 **Ready to deploy!**

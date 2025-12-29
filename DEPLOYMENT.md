# Render Deployment Guide 🚀

## Files Created for Deployment

✅ `.streamlit/config.toml` - Streamlit server configuration
✅ `Procfile` - Process file for Render
✅ `start.sh` - Startup script

## Step-by-Step Deployment

### 1. Push to GitHub

```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### 2. Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in the details:
   - **Name:** `daily-habit-tracker`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

### 3. Set Environment Variables

In Render dashboard, go to **Environment** tab and add these variables from your `.env` file:

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

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

**⚠️ Important:** Add all users you want to have access!

### 4. Deploy

Click **"Create Web Service"** and Render will:
- Clone your repository
- Install dependencies
- Start the Streamlit app
- Provide a public URL (e.g., `https://daily-habit-tracker.onrender.com`)

### 5. Access Your App

- Visit the URL provided by Render
- Log in with any of the configured usernames/passwords
- Share the URL with friends who are configured in environment variables!

## Troubleshooting

### Error: "Failed to fetch dynamically imported module"
✅ **Fixed!** The `.streamlit/config.toml` file resolves this.

### Error: "Port already in use"
- Render automatically assigns `$PORT`, no action needed

### Database not persisting
- Render's free tier uses ephemeral storage
- Consider upgrading to a paid plan or using an external database (PostgreSQL)
- For now, data will reset on each deploy

### Can't login
- Double-check environment variables are set correctly in Render
- Make sure variable names match exactly (case-sensitive)

## Adding More Users

1. Go to Render dashboard → Your service → **Environment**
2. Add new variables:
   ```
   USER_4_USERNAME=newuser
   USER_4_PASSWORD=newpass
   USER_4_DISPLAYNAME=New User 🎯
   ```
3. Click **"Save Changes"**
4. Render will automatically restart the app

## Free Tier Limitations

- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Database resets on each deploy
- 750 hours/month free (enough for 24/7 if only one app)

## Production Recommendations

For serious use:
1. Upgrade to Render paid plan ($7/month)
2. Add PostgreSQL database for persistent storage
3. Set up automatic backups
4. Use stronger passwords
5. Add rate limiting

---

**Your app is now live! Share with friends and start tracking habits together! 🎉**

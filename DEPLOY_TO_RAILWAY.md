# 🚀 Deploy Italian Learning Companion to Railway

**Time Required:** 15 minutes
**Cost:** ~$5/month for small group usage
**Difficulty:** Easy (3 steps!)

---

## ✅ Prerequisites (You Already Have These!)

- ✅ GitHub account (Jgcarrier)
- ✅ GitHub repository with code pushed
- ✅ Domain name (your WordPress domain)
- ✅ Credit/debit card for Railway (free $5 credit first!)

---

## 🎯 Step 1: Create Railway Account & Deploy (5 min)

### 1.1 Sign Up for Railway

1. Go to: **https://railway.app**
2. Click **"Start a New Project"** or **"Login"**
3. Choose **"Login with GitHub"**
4. Authorize Railway to access your GitHub account
5. You get **$5 free credit** (no card required yet!)

### 1.2 Deploy Your App

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: **`Jgcarrier/italian-learning-companion`**
4. Railway will automatically detect it's a Flask app
5. Click **"Deploy"**

**That's it!** Railway will:
- Install Python dependencies
- Set up the database
- Start your app with gunicorn
- Give you a URL (e.g., `italian-learning-companion-production.up.railway.app`)

### 1.3 Wait for Deployment (2-3 minutes)

Watch the logs in Railway dashboard:
```
Building...
Installing dependencies...
Starting gunicorn...
✅ Deployed successfully!
```

Click the **generated URL** to test your app!

---

## 🔐 Step 2: Set Environment Variables (2 min)

For security, set a secret key:

1. In Railway dashboard, click your **project**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   ```
   SECRET_KEY = your-super-secret-random-string-here
   ```
   (Make it random, like: `aB3xK9mP2qR8sT5vW7yZ1nC4dF6gH0j`)
5. Click **"Deploy"** (Railway will restart with new variable)

---

## 🌐 Step 3: Connect Your Domain (5 min)

### Option A: Subdomain (Recommended - Easiest)

Use a subdomain like: `italian.yourdomain.com`

**In Railway:**
1. Click **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"+ Custom Domain"**
4. Enter: `italian.yourdomain.com`
5. Railway gives you a **CNAME target** (e.g., `italian-xyz.up.railway.app`)

**In Your Domain DNS (wherever you manage DNS):**
1. Log into your domain provider (GoDaddy, Namecheap, etc.)
2. Go to **DNS Settings**
3. Add a **CNAME record**:
   ```
   Type: CNAME
   Name: italian
   Value: [the target Railway gave you]
   TTL: 3600 (or Auto)
   ```
4. Click **Save**

**Wait 5-30 minutes** for DNS to propagate.

Then visit: **https://italian.yourdomain.com** 🎉

### Option B: Add to WordPress Page

If you want it to appear within WordPress:

**Embed in WordPress Page:**
1. Create new page in WordPress
2. Add **HTML block**
3. Add this code:
   ```html
   <iframe
     src="https://italian.yourdomain.com"
     width="100%"
     height="800px"
     frameborder="0">
   </iframe>
   ```
4. Publish page

**Or Link from WordPress:**
Just add a button/link pointing to `https://italian.yourdomain.com`

---

## 💰 Step 4: Add Payment Method (When Free Credit Runs Out)

Railway gives you **$5 free credit**. When that's used:

1. Go to **Account Settings**
2. Click **"Billing"**
3. Add **credit/debit card**
4. Set **usage limit** (recommended: $10/month)

**Your cost** for small group:
- Light usage: **$5/month**
- Medium usage: **$8/month**
- Heavy usage: **$12/month**

You're charged **only for what you use** (no flat fee).

---

## 🔄 Future Updates (Auto-Deploy!)

When you make changes to your app:

1. **Make changes locally**
2. **Commit to git**: `git commit -m "My changes"`
3. **Push to GitHub**: `git push`
4. **Railway auto-deploys!** (30 seconds later, your site updates)

✨ No need to touch Railway - it watches your GitHub!

---

## ✅ Testing Checklist

After deployment, test:

- [ ] App loads at Railway URL
- [ ] Can select a level (A1, A2, etc.)
- [ ] Can start a practice session
- [ ] Can answer questions
- [ ] Can complete a practice session
- [ ] Can navigate back to home
- [ ] Custom domain works (if set up)

---

## 🆘 Troubleshooting

### "Application Error" on Railway

**Check Logs:**
1. Railway dashboard → **"Deployments"** tab
2. Click latest deployment
3. View logs for errors

**Common fixes:**
- Make sure `Procfile` exists
- Check `requirements.txt` has all dependencies
- Verify `gunicorn` is in requirements.txt

### Database Not Working

The SQLite database is in the repo, so it should work.

If issues:
1. Check Railway logs for "database locked" errors
2. SQLite is fine for small groups (<50 concurrent users)
3. For more users, consider upgrading to PostgreSQL (Railway makes this easy)

### Custom Domain Not Working

**Wait longer:**
- DNS can take 5-60 minutes to propagate
- Try in incognito/private browsing

**Check DNS:**
- Use https://dnschecker.org
- Enter your domain
- Should show CNAME pointing to Railway

**Common issues:**
- Wrong CNAME value (double-check Railway's value)
- Still pointing to old host
- Need to clear browser cache

---

## 📊 Monitoring Usage & Costs

**Check usage:**
1. Railway dashboard → **"Metrics"** tab
2. See: CPU, Memory, Network usage
3. Estimated monthly cost shown

**Set alerts:**
1. Account Settings → **"Usage Limits"**
2. Set **monthly spend limit** (e.g., $10)
3. Railway stops service if limit hit (protects from surprise bills)

---

## 🎓 Sharing with Italian Class

Once deployed:

### Share the Link:
```
Hey! I built an Italian practice app.
Try it out: https://italian.yourdomain.com

- Choose your level (A1, A2, etc.)
- Pick a practice type
- Get instant feedback!
```

### Usage Tips for Classmates:
- No account needed - just start practicing
- Works on phones, tablets, laptops
- Don't type accents (à, è) - just type regular letters (a, e)
- Use digits for numbers: "27" works for "twenty-seven"
- Sentence translations are lenient - capture the meaning!

---

## 🚀 Next Steps After Deployment

### Optional Enhancements:

1. **Add Google Analytics** (track usage)
2. **Set up monitoring** (uptime alerts)
3. **Add more content** (B1/B2 vocabulary)
4. **User accounts** (track individual progress - future)
5. **Mobile app** (wrap in Capacitor - future)

### Railway Features You Might Like:

- **PR Previews**: Test changes before merging
- **Automatic SSL**: HTTPS included free
- **Zero Downtime Deploys**: App stays up during updates
- **Easy Rollbacks**: Revert to previous version in 1 click

---

## 📞 Support

**Railway Support:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**Your App Support:**
- GitHub Issues: https://github.com/Jgcarrier/italian-learning-companion/issues
- You can ask me for help anytime!

---

## 🎉 Success!

Once deployed, you'll have:

✅ Professional Italian learning app
✅ Live on the internet
✅ Custom domain (italian.yourdomain.com)
✅ Auto-deploys when you push to GitHub
✅ Costs ~$5/month
✅ Share with unlimited classmates

**Congratulations!** 🇮🇹🚀

---

**Questions?** Just ask - I'm here to help with any step!

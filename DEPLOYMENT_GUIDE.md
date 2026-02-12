# 🚀 Deployment Guide - Italian Learning Companion

## Complete Deployment Plan for Web Server

Your Italian Learning Companion is ready to deploy to a web server! Here's a comprehensive step-by-step guide.

---

## 📋 What You're Deploying

**14 Complete Practice Modules:**
1. Vocabulary Quiz
2. Verb Conjugation
3. Irregular Passato Prossimo
4. Avere vs Essere
5. Futuro Semplice
6. Reflexive Verbs
7. Articulated Prepositions
8. Time Prepositions
9. Negations
10. Fill in the Blank
11. Multiple Choice
12. **Sentence Translator (NEW!)**
13. Progress Stats
14. Topic List

---

## 🎯 Deployment Options

### Option 1: **DigitalOcean App Platform** (Recommended - Easiest)
- **Cost:** $5-12/month
- **Complexity:** ⭐ Very Easy
- **Setup Time:** 15 minutes
- **Best for:** Quick deployment, automatic SSL, no server management

### Option 2: **Heroku**
- **Cost:** $5-7/month (Eco Dyno)
- **Complexity:** ⭐ Very Easy
- **Setup Time:** 20 minutes
- **Best for:** Simple deployment, familiar platform

### Option 3: **DigitalOcean Droplet** (Traditional VPS)
- **Cost:** $6/month
- **Complexity:** ⭐⭐⭐ Medium
- **Setup Time:** 1-2 hours
- **Best for:** Full control, learning server management

### Option 4: **Railway.app**
- **Cost:** $5/month
- **Complexity:** ⭐ Very Easy
- **Setup Time:** 10 minutes
- **Best for:** Modern, developer-friendly platform

### Option 5: **PythonAnywhere**
- **Cost:** $5/month
- **Complexity:** ⭐⭐ Easy
- **Setup Time:** 30 minutes
- **Best for:** Python-specific hosting

---

## 🏆 RECOMMENDED: DigitalOcean App Platform

This is the easiest option with professional results.

### Step-by-Step Deployment:

#### 1. **Prepare Your Code for Deployment**

First, create necessary deployment files:

```bash
cd ~/Desktop/Parkinglot/Code-Projects/italian-learning-companion
```

**Create `requirements.txt`:**
```bash
cd web_app
cat > requirements.txt << 'EOF'
Flask==3.1.2
gunicorn==21.2.0
EOF
```

**Create `Procfile`:**
```bash
cat > Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:$PORT app:app
EOF
```

**Create `runtime.txt`:**
```bash
cat > runtime.txt << 'EOF'
python-3.11.6
EOF
```

**Update `app.py` for production:**

Change the last line from:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

To:
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
```

**Update secret key:**
In `app.py`, change:
```python
app.secret_key = 'italian-learning-companion-secret-key-2024'
```

To:
```python
import os
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
```

#### 2. **Create a Git Repository**

```bash
cd ~/Desktop/Parkinglot/Code-Projects/italian-learning-companion

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
*.so
*.egg
*.egg-info/
dist/
build/
.DS_Store
.env
EOF

# Add all files
git add .

# Commit
git commit -m "Initial commit - Italian Learning Companion"
```

#### 3. **Push to GitHub**

1. Go to https://github.com
2. Click "New Repository"
3. Name it: `italian-learning-companion`
4. Don't initialize with README
5. Click "Create Repository"

Then push your code:

```bash
git remote add origin https://github.com/YOUR_USERNAME/italian-learning-companion.git
git branch -M main
git push -u origin main
```

#### 4. **Deploy to DigitalOcean App Platform**

1. **Sign up for DigitalOcean:**
   - Go to https://www.digitalocean.com
   - Sign up (they often have $200 free credit for new users)

2. **Create New App:**
   - Click "Create" → "App Platform"
   - Choose "GitHub" as source
   - Authorize DigitalOcean to access your GitHub
   - Select `italian-learning-companion` repository
   - Branch: `main`
   - Autodeploy: ✅ Enable

3. **Configure App:**
   - **Name:** italian-learning-companion
   - **Region:** Choose closest to you (e.g., London for UK)
   - **Plan:** Basic - $5/month
   - **Instance Size:** Basic (512MB RAM)

4. **Environment Variables:**
   - Click "Edit" next to Environment Variables
   - Add: `SECRET_KEY` = (generate a random string like `your-random-secret-key-here-12345`)

5. **Review and Deploy:**
   - Review settings
   - Click "Create Resources"
   - Wait 5-10 minutes for deployment

6. **Your App is Live!**
   - You'll get a URL like: `https://italian-learning-companion-xxxxx.ondigitalocean.app`
   - Test it in your browser!

---

## 🔧 Alternative: Railway.app (Very Modern & Easy)

Railway is great for modern deployments.

### Quick Deployment:

1. **Sign up:** https://railway.app
2. **New Project:** Click "New Project" → "Deploy from GitHub"
3. **Connect GitHub:** Authorize Railway
4. **Select Repository:** Choose `italian-learning-companion`
5. **Configure:**
   - Add environment variable: `SECRET_KEY` = random string
   - Railway auto-detects Python/Flask
6. **Deploy:** Click deploy
7. **Get URL:** Railway provides a URL like `italian-learning-companion.up.railway.app`

**Cost:** $5/month

---

## 🛠️ Alternative: Traditional VPS (DigitalOcean Droplet)

For those who want full control.

### Step-by-Step:

#### 1. Create Droplet
- Sign up at DigitalOcean
- Create Droplet: Ubuntu 22.04, Basic plan, $6/month
- Add SSH key
- Create Droplet

#### 2. SSH Into Server
```bash
ssh root@your_server_ip
```

#### 3. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3 python3-pip python3-venv nginx -y

# Install supervisor (process manager)
apt install supervisor -y
```

#### 4. Set Up Application
```bash
# Create app user
adduser italianapp
usermod -aG sudo italianapp
su - italianapp

# Clone repository
cd /home/italianapp
git clone https://github.com/YOUR_USERNAME/italian-learning-companion.git
cd italian-learning-companion

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd web_app
pip install -r requirements.txt
pip install gunicorn
```

#### 5. Configure Gunicorn
```bash
# Create gunicorn config
cat > /home/italianapp/italian-learning-companion/web_app/gunicorn_config.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 2
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
EOF

# Create log directory
sudo mkdir -p /var/log/gunicorn
sudo chown italianapp:italianapp /var/log/gunicorn
```

#### 6. Configure Supervisor
```bash
sudo cat > /etc/supervisor/conf.d/italian-learning.conf << 'EOF'
[program:italian-learning]
command=/home/italianapp/italian-learning-companion/venv/bin/gunicorn -c gunicorn_config.py app:app
directory=/home/italianapp/italian-learning-companion/web_app
user=italianapp
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/gunicorn/error.log
stdout_logfile=/var/log/gunicorn/access.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start italian-learning
```

#### 7. Configure Nginx
```bash
sudo cat > /etc/nginx/sites-available/italian-learning << 'EOF'
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/italianapp/italian-learning-companion/web_app/static;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/italian-learning /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Set Up SSL (Optional but Recommended)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

---

## 🔒 Security Checklist

Before going live:

- [ ] Change `SECRET_KEY` to a random string
- [ ] Set `debug=False` in production
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall (if using VPS)
- [ ] Regular backups of database
- [ ] Update dependencies regularly

---

## 📊 Post-Deployment

### Monitor Your App:
- Check logs regularly
- Monitor resource usage
- Set up uptime monitoring (UptimeRobot.com - free)

### Updates:
```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push

# Most platforms auto-deploy on git push
# For VPS, SSH in and:
cd /home/italianapp/italian-learning-companion
git pull
sudo supervisorctl restart italian-learning
```

---

## 💰 Cost Summary

| Platform | Monthly Cost | Ease | Recommended |
|----------|-------------|------|-------------|
| DigitalOcean App | $5-12 | ⭐ | ✅ Yes |
| Railway | $5 | ⭐ | ✅ Yes |
| Heroku | $5-7 | ⭐ | ✅ Yes |
| DigitalOcean Droplet | $6 | ⭐⭐⭐ | For learning |
| PythonAnywhere | $5 | ⭐⭐ | Good option |

---

## 🎯 Recommended Path

**For You:** I recommend **Railway.app** or **DigitalOcean App Platform**

**Why:**
- Dead simple deployment (10-15 minutes)
- Automatic HTTPS
- Auto-deploys from GitHub
- No server management
- Professional results
- Very affordable

**Next Steps:**
1. Create the deployment files (shown above)
2. Push to GitHub
3. Deploy to Railway or DigitalOcean App
4. Share your live URL!

---

## 📞 Need Help?

Common issues and solutions are in the troubleshooting section of each platform's docs. The app is production-ready as-is!

**Your app is ready to go live! 🚀**

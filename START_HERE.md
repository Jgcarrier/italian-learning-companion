# 🇮🇹 Italian Learning Companion - Web App

## ✅ Server is Running!

Your Flask web app is now live at:

### 🖥️ On This Computer:
**http://localhost:5001**

### 📱 On Mobile (Same WiFi):
**http://Macmini.vodafone.ultrahub:5001**

---

## 🎯 Try It Now:

1. **Open your browser** and go to http://localhost:5001
2. **Click "Vocabulary Quiz"**
3. **Choose settings:**
   - Direction: Italian → English (or English → Italian)
   - Questions: 10 (or any number you like)
4. **Click "Start Quiz"**
5. **Type your answers** - no need for accents!
   - Type "caffe" instead of "caffè" ✅
   - Type "citta" instead of "città" ✅
6. **Get instant feedback** ✅ or ❌
7. **See your results** with score, time, and grade!

---

## 📊 What's Available:

### ✅ Working Now:
- **Vocabulary Quiz** - Full practice flow with accent-forgiving input
- **Progress Stats** - View your 7/30/90 day performance
- **Topic List** - Browse all A1 and A2 topics

### 🔄 Coming Soon:
- Verb Conjugation Practice
- Irregular Passato Prossimo
- Avere vs Essere Choice
- Futuro Semplice
- Reflexive Verbs
- Articulated Prepositions
- Time Prepositions
- Negations
- Fill in the Blank
- Multiple Choice

---

## 🎨 Features:

- **Mobile Responsive** - Works great on phone and desktop
- **Accent Forgiving** - Perfect for your UK keyboard
- **Immediate Feedback** - Know right away if you're correct
- **Progress Tracking** - All sessions saved to database
- **Clean Design** - Duolingo-style, Italian flag colors

---

## 🛑 To Stop the Server:

The server is running in the background. To stop it:

1. Find the process:
   ```bash
   lsof -ti:5001
   ```

2. Kill it:
   ```bash
   kill $(lsof -ti:5001)
   ```

Or simply restart your computer.

---

## 🔄 To Restart the Server:

```bash
cd ~/Desktop/Parkinglot/Code-Projects/italian-learning-companion/web_app
./run.sh
```

---

## 📖 More Information:

- **GETTING_STARTED.md** - Detailed usage guide
- **README.md** - Technical overview
- **test_app.py** - Run tests to verify everything works

---

**Enjoy practicing Italian! 🇮🇹**

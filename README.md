# 🇮🇹 Italian Learning Companion - Web App

A comprehensive web-based Italian language learning platform with multiple practice modules and difficulty levels.

## ✨ Features

### 5 Difficulty Levels
- 🌱 **A1 - Beginner**: First steps in Italian
- 🌿 **A2 - Elementary**: Everyday topics and phrases
- 🌳 **B1 - Intermediate**: Express opinions and ideas
- 🏔️ **B2 - Upper Intermediate**: Detailed arguments
- 🎓 **GCSE**: UK exam preparation focus

### 12 Practice Types

**Verbs:**
- ✅ General Verb Conjugation
- ✅ Irregular Passato Prossimo
- ✅ Avere vs Essere (Auxiliary Choice)
- ✅ Futuro Semplice
- ✅ Reflexive Verbs

**Vocabulary:**
- ✅ Italian → English Quiz
- ✅ English → Italian Quiz
- ✅ Sentence Translation (IT→EN)
- ✅ Sentence Translation (EN→IT)

**Grammar:**
- ✅ Articulated Prepositions
- ✅ Time Prepositions
- ✅ Negations

**Mixed Practice:**
- ✅ Fill in the Blank
- ✅ Multiple Choice

### Smart Features
- ✅ **Accent-forgiving input** - "caffe" = "caffè"
- ✅ **Flexible answer matching** - "small" OR "low" for "small/low"
- ✅ **Optional "to" prefix** - "speak" = "to speak"
- ✅ **Punctuation-free sentences** - No punctuation required
- ✅ **Intelligent keyword matching** - 70% threshold for sentences
- ✅ **Mobile responsive design**
- ✅ **Progress tracking**
- ✅ **Immediate feedback**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd italian-learning-companion/web_app
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the app**:
```bash
./run.sh
```

Or manually:
```bash
python3 app.py
```

4. **Access the app**:
- **Desktop**: http://localhost:5001
- **Mobile** (same network): http://YOUR_LOCAL_IP:5001

## 📁 Project Structure

```
web_app/
├── app.py                 # Main Flask application
├── database.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── run.sh                # Startup script
├── static/
│   └── css/
│       └── style.css     # Italian flag-themed styling
├── templates/            # HTML templates
│   ├── base.html
│   ├── level_select.html
│   ├── category_menu.html
│   ├── *_menu.html       # Category submenus
│   ├── *_setup.html      # Practice setup pages
│   ├── question.html
│   ├── feedback.html
│   └── summary.html
└── ../src/              # Shared modules
    ├── database.py      # Database operations
    └── practice_generator.py  # Question generation
```

## 🎯 Usage

### Navigation Flow
1. **Choose your level** (A1, A2, B1, B2, or GCSE)
2. **Select a category** (Verbs, Vocabulary, Grammar, Mixed)
3. **Pick a practice type**
4. **Configure settings** (number of questions, direction, etc.)
5. **Start practicing!**

### Example Flows
```
Home → A1 → Vocabulary → IT→EN Quiz → Practice
Home → B1 → Verbs → Futuro Semplice → Practice
Home → GCSE → Grammar → Time Prepositions → Practice
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Mobile-responsive)
- **Session Management**: Flask Sessions
- **Styling**: Italian flag colors (#009246 green, #CE2B37 red)

## 📊 Database Content

- **200+ vocabulary items** across all levels
- **60+ translation sentences**
- **Verb conjugations** for all common tenses
- **Grammar rules** and exercises
- **Topic-based organization**

## 🔮 Deployment

See `DEPLOYMENT_GUIDE.md` for detailed instructions on deploying to:
- Railway.app
- DigitalOcean App Platform
- Heroku
- DigitalOcean Droplet
- PythonAnywhere

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add more vocabulary
- Create new practice types
- Improve the UI/UX
- Add new difficulty levels
- Fix bugs

## 🙏 Acknowledgments

Built with ❤️ for Italian language learners everywhere!

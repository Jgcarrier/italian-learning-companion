# Getting Started with Italian Learning Companion Web App

## Quick Start

1. **Start the server:**
   ```bash
   cd ~/Desktop/Parkinglot/Code-Projects/italian-learning-companion/web_app
   ./run.sh
   ```

   Or manually:
   ```bash
   python3 app.py
   ```

2. **Open in browser:**
   - On your computer: http://localhost:5000
   - On your phone (same WiFi): http://[your-computer-ip]:5000

3. **Try the Vocabulary Quiz:**
   - Click "Vocabulary Quiz" on home page
   - Choose Italian→English or English→Italian
   - Select number of questions (default 10)
   - Click "Start Quiz"
   - Type your answers (no need for accents!)
   - Get immediate feedback
   - View your results and stats

## What's Working Now

### ✅ Vocabulary Quiz (Complete Flow)
- Choose direction (IT→EN or EN→IT)
- Configure number of questions
- Answer questions one by one
- **Accent-forgiving input** - type "caffe" for "caffè"
- Immediate visual feedback (✅/❌)
- Shows proper spelling after submission
- Auto-advances to next question (2 seconds)
- Summary with score, accuracy, time, grade
- Results saved to database

### ✅ Progress Stats
- View sessions, questions, accuracy for 7/30/90 days
- See weak areas that need practice

### ✅ Topic List
- Browse all A1 and A2 topics
- See completion status
- View descriptions and lesson references

## Design Features

### Mobile Responsive
- Large, tap-friendly buttons
- Responsive grid layout
- Works great on phones and tablets

### User-Friendly
- No need to type Italian accents (à, è, ì, ò, ù)
- Clean, Duolingo-style interface
- Italian flag colors as accents (not overwhelming)
- Immediate visual feedback

### Database Integration
- Reuses existing SQLite database
- 200+ vocabulary words
- Tracks all practice sessions
- Performance analytics

## Project Structure

```
web_app/
├── app.py                          # Flask application (main logic)
├── run.sh                          # Convenience script to start server
├── test_app.py                     # Test script to verify setup
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview
├── GETTING_STARTED.md             # This file
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base layout
│   ├── home.html                   # Main menu (13 options)
│   ├── vocabulary_quiz_setup.html  # Quiz configuration
│   ├── question.html               # Question display
│   ├── feedback.html               # Answer feedback
│   ├── summary.html                # Session results
│   ├── stats.html                  # Progress statistics
│   └── topics.html                 # Topic list
│
└── static/
    └── css/
        └── style.css               # All styling
```

## Technical Details

### Accent Normalization
The `remove_accents()` function converts both user input and correct answers to non-accented form for comparison:
- User types: "caffe"
- System compares: "caffe" == "caffe" ✅
- Shows: "Proper spelling: caffè"

### Session Management
Flask sessions track the current practice:
- `questions`: List of generated questions
- `current_question`: Index of current question
- `correct_count`: Running score
- `answers`: Complete history for review
- `start_time`: For time tracking

### Database Reuse
Imports existing modules from `src/`:
- `database.py` → ItalianDatabase class
- `practice_generator.py` → PracticeGenerator class
- Same `curriculum.db` used by terminal app

## Next Steps

### Adding More Practice Types

The codebase is set up so adding new practice types is straightforward. Each type follows the same pattern:

1. **Add route in `app.py`:**
   ```python
   @app.route('/new-practice', methods=['GET', 'POST'])
   def new_practice():
       # Setup form (GET) or start session (POST)
       questions = generator.generate_new_practice_type(...)
       # Store in session and redirect to practice_question
   ```

2. **Create setup template** (if needed):
   ```html
   <!-- templates/new_practice_setup.html -->
   <form method="POST">
       <!-- Configuration options -->
   </form>
   ```

3. **Update home.html:**
   ```html
   <a href="{{ url_for('new_practice') }}" class="menu-item">
       <div class="menu-icon">🎯</div>
       <h3>New Practice Type</h3>
   </a>
   ```

4. **Test it!**

The existing `question.html`, `feedback.html`, and `summary.html` templates are reusable for all practice types.

### Priority Order for Implementation

Based on your usage of the terminal app, I suggest implementing in this order:

1. **Auxiliary Choice** (avere vs essere) - high value, unique explanations
2. **Time Prepositions** (per/da/a/fa) - high value, unique explanations
3. **Irregular Passato Prossimo** - frequently used
4. **Futuro Semplice** - frequently used
5. **Reflexive Verbs** - frequently used
6. **Articulated Prepositions** - good practice
7. **Negations** - with explanations
8. **Multiple Choice** - mixed practice
9. **General Verb Conjugation** - covered by others
10. **Fill in the Blank** - mixed practice

## Testing Checklist

Before deploying each new practice type:

- [ ] Can select difficulty/count
- [ ] Questions generate correctly
- [ ] Accent normalization works
- [ ] Feedback shows correct/incorrect
- [ ] Special explanations display (if applicable)
- [ ] Summary shows accurate stats
- [ ] Session saves to database
- [ ] Mobile layout works
- [ ] Back button works
- [ ] Can practice again

## Troubleshooting

**App won't start:**
```bash
cd ~/Desktop/Parkinglot/Code-Projects/italian-learning-companion/web_app
python3 test_app.py  # Run tests to identify issue
```

**No questions appearing:**
- Check database has data: `sqlite3 ../data/curriculum.db "SELECT COUNT(*) FROM vocabulary;"`
- Verify imports work: `python3 -c "from database import ItalianDatabase; print('OK')"`

**Mobile can't connect:**
- Make sure phone is on same WiFi network
- Check firewall isn't blocking port 5000
- Use computer's IP address, not "localhost"

## Tips for Development

1. **Auto-reload:** Flask runs in debug mode, so changes to Python/HTML/CSS will auto-reload
2. **Testing:** Use `python3 test_app.py` to verify setup after making changes
3. **Database:** Original `data/curriculum.db` is shared with terminal app - changes affect both
4. **Styling:** All CSS in one file (`static/css/style.css`) for easy customization
5. **Mobile testing:** Use your phone for real mobile testing, not just browser resize

Enjoy building out the rest of the app! 🇮🇹

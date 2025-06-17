# **Card Drawing Simulator**
A complete web application that allows users to draw cards, manage their collection, and explore other users' collections.
Developed in Python (Flask) for backend and HTML/CSS/JavaScript for frontend.
## Main Features
- Authentication (sign up, log in, log out)
- Draws limited to 30 per day (auto-upgrade every day)
- Visualization of the cards drawn
- Backup and management of cards in the user collection
- Ability to set a favorite card
- Browsing other users' collections
- Card deletion (get 1 draw every 2 cards deleted)
- Simple, fluid, and fast responsive interface

## Technologies used
### Backend
- Python 3
- Flask
- SQLAlchemy (ORM)
- SQLite
- Jinja2 (templates)
- External API tcgdex.net for Pokémon cards

### Frontend
- HTML CSS
- JavaScript
- LocalStorage (for the client-side daily reset logic)

## Installation
### Clone the project
`git clone https://github.com/IncendieForet/CardSimulator.git`
### Install the required dependencies
`pip install -r requirements.txt`
### Run the application
`python app.py`
### Go to http://127.0.0.1:5000

## Operation of the daily reset
The browser checks via localStorage the last connection date.
If it’s a new day, it sends a request to /set_tir to reset the number of draws to 30 if the user had less.

## `User` Database
```
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tir = db.Column(db.Integer, default=30)
    cards = db.Column(JSON, default=list)
```

## Examples of backend logic
- `/tirage` : draws random cards via the Pokémon API
- `/delete` : deletes cards from the collection
- `/favorite` : bookmarks a card (1st position in the list)
- `/collections` : displays all the collections with the user's favorite card
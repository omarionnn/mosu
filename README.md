# MOSU - Collaborative Food Ordering Platform

MOSU is a web-based platform that simplifies group food ordering by allowing multiple users to collaboratively create and manage food orders in real-time.

## Features

- **User Authentication**
  - Secure signup and login
  - Session management
  - User-specific data isolation

- **Order Management**
  - Create orders with unique 4-digit PINs
  - Join existing orders using PINs
  - Real-time cart management
  - Leave order functionality

- **Multi-User Support**
  - Multiple users can join the same order
  - Individual cart tracking per user
  - Collaborative order building

- **Comprehensive Receipt Generation**
  - Items grouped by user
  - Individual subtotals
  - Group total calculation
  - Order details and timestamp

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Styling**: Tailwind CSS

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd mvpbo
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python3
>>> from app import db
>>> db.create_all()
>>> exit()
```

5. Run the application:
```bash
python3 app.py
```

The application will be available at `http://localhost:9091`

## Usage

1. **Create an Order**:
   - Sign up or log in
   - Click "Create Order"
   - Share the PIN with your group

2. **Join an Order**:
   - Log in to your account
   - Enter the order PIN
   - Start adding items to your cart

3. **Generate Receipt**:
   - Click "Generate Receipt" to see all items
   - View individual and group totals

## Security Features

- Password hashing
- Session-based authentication
- Input validation
- Secure error handling

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[MIT License](LICENSE)

## Author

Omar Inyarko

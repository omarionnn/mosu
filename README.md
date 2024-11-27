# Big Orders - Collaborative Food Ordering Platform

A web application that streamlines group food ordering with advanced cart management and receipt generation features.

🌐 **Live Demo**: [https://bigorders.onrender.com](https://bigorders.onrender.com)

## Features

- 👥 **User Management**
  - Sign up with email
  - Secure login/logout
  - Session management

- 🛒 **Order Management**
  - Create new orders with custom names
  - Join existing orders using PIN
  - Leave orders
  - Multiple users can collaborate on one order

- 🍽️ **Cart Features**
  - Add items to cart
  - Update quantities
  - Remove items
  - User-specific cart tracking

- 📝 **Receipt Generation**
  - Detailed receipt per order
  - Items grouped by user
  - Individual subtotals
  - Order grand total

## Technology Stack

- Backend: Flask (Python)
- Frontend: Vanilla JavaScript
- Database: SQLite with SQLAlchemy ORM
- Authentication: Flask-Login

## Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/omarionnn/mosu.git
   cd mosu
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   # The database will be automatically initialized when you run the app
   # It will create tables and add sample menu items
   ```

5. **Run the Application**
   ```bash
   python3 app.py
   ```

6. **Access the Application**
   - Open your browser and go to `http://localhost:9091`
   - The sample menu items will be automatically added on first run

## Production Deployment

The application is deployed on Render.com. To deploy your own instance:

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Python Version: 3.11.0

## Environment Variables

For production deployment, set these environment variables:
- `FLASK_ENV`: Set to `production`
- `FLASK_APP`: Set to `app.py`
- `SECRET_KEY`: Set to a secure random string

## Database Schema

- **User**: Stores user information and authentication details
- **Order**: Manages order information including PIN and status
- **MenuItem**: Stores available menu items
- **OrderItem**: Tracks items added to orders with quantities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this project as you wish.

## Support

For issues or feature requests, please create an issue in the GitHub repository.

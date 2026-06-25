"""
AI Finance Advisor - Flask Backend
Modern financial management application with AI advisory
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from google import genai
import os
from functools import wraps
from dotenv import load_dotenv
load_dotenv()


# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_advisor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize Extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User model for authentication and account management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # 'personal' or 'business'
    business_name = db.Column(db.String(255))
    business_type = db.Column(db.String(120))
    gemini_api_key = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'account_type': self.account_type,
            'business_name': self.business_name,
            'business_type': self.business_type,
            'created_at': self.created_at.isoformat()
        }


class Transaction(db.Model):
    """Transaction model for recording income and expenses"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'type': self.type,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validation
    if not all(k in data for k in ['name', 'email', 'password', 'account_type']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        name=data['name'],
        email=data['email'],
        account_type=data['account_type'],
        business_name=data.get('business_name'),
        business_type=data.get('business_type')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing credentials'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


# ============================================================================
# TRANSACTION ROUTES
# ============================================================================

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transactions with optional filtering"""
    user_id = get_jwt_identity()
    
    # Query parameters
    tx_type = request.args.get('type')  # 'income', 'expense', or None for all
    category = request.args.get('category')
    month = request.args.get('month')  # Format: YYYY-MM
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if tx_type:
        query = query.filter_by(type=tx_type)
    
    if category:
        query = query.filter_by(category=category)
    
    if month:
        year, month_num = map(int, month.split('-'))
        start_date = datetime(year, month_num, 1).date()
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month_num + 1, 1).date()
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    return jsonify([tx.to_dict() for tx in transactions]), 200


@app.route('/api/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    """Add a new transaction"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validation
    required_fields = ['date', 'type', 'category', 'amount']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['type'] not in ['income', 'expense']:
        return jsonify({'error': 'Invalid transaction type'}), 400
    
    try:
        date = datetime.fromisoformat(data['date']).date()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Amount must be a positive number'}), 400
    
    transaction = Transaction(
        user_id=user_id,
        date=date,
        type=data['type'],
        category=data['category'],
        amount=amount,
        description=data.get('description'),
        notes=data.get('notes')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction added successfully',
        'transaction': transaction.to_dict()
    }), 201


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """Update a transaction"""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'date' in data:
        try:
            transaction.date = datetime.fromisoformat(data['date']).date()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format'}), 400
    
    if 'type' in data:
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': 'Invalid transaction type'}), 400
        transaction.type = data['type']
    
    if 'category' in data:
        transaction.category = data['category']
    
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                raise ValueError
            transaction.amount = amount
        except (ValueError, TypeError):
            return jsonify({'error': 'Amount must be a positive number'}), 400
    
    if 'description' in data:
        transaction.description = data['description']
    
    if 'notes' in data:
        transaction.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction updated successfully',
        'transaction': transaction.to_dict()
    }), 200


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction"""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted successfully'}), 200


# ============================================================================
# FINANCIAL METRICS ROUTES
# ============================================================================

@app.route('/api/metrics/summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    """Get financial summary (total balance, income, expenses, net balance)"""
    user_id = get_jwt_identity()
    
    # Optional month filter
    month = request.args.get('month')  # Format: YYYY-MM
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if month:
        year, month_num = map(int, month.split('-'))
        start_date = datetime(year, month_num, 1).date()
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month_num + 1, 1).date()
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    transactions = query.all()
    
    total_income = sum(tx.amount for tx in transactions if tx.type == 'income')
    total_expense = sum(tx.amount for tx in transactions if tx.type == 'expense')
    net_balance = total_income - total_expense
    
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'transaction_count': len(transactions)
    }), 200


@app.route('/api/metrics/category-breakdown', methods=['GET'])
@jwt_required()
def get_category_breakdown():
    """Get spending/income breakdown by category"""
    user_id = get_jwt_identity()
    
    month = request.args.get('month')
    tx_type = request.args.get('type')  # 'income' or 'expense'
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if tx_type:
        query = query.filter_by(type=tx_type)
    
    if month:
        year, month_num = map(int, month.split('-'))
        start_date = datetime(year, month_num, 1).date()
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month_num + 1, 1).date()
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    transactions = query.all()
    
    # Group by category
    breakdown = {}
    for tx in transactions:
        if tx.category not in breakdown:
            breakdown[tx.category] = 0
        breakdown[tx.category] += tx.amount
    
    return jsonify(breakdown), 200


@app.route('/api/metrics/monthly-trend', methods=['GET'])
@jwt_required()
def get_monthly_trend():
    """Get monthly income and expense trends (last 12 months)"""
    user_id = get_jwt_identity()
    
    # Calculate 12 months of data
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    query = Transaction.query.filter_by(user_id=user_id).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # Group by month
    monthly_data = {}
    for tx in query:
        month_key = tx.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if tx.type == 'income':
            monthly_data[month_key]['income'] += tx.amount
        else:
            monthly_data[month_key]['expense'] += tx.amount
    
    return jsonify(monthly_data), 200


@app.route('/api/metrics/update-api-key', methods=['POST'])
@jwt_required()
def update_gemini_api_key():
    """Update user's Gemini API key"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    user.gemini_api_key = api_key
    db.session.commit()
    
    return jsonify({'message': 'API key updated successfully'}), 200


# ============================================================================
# AI ADVISOR ROUTES
# ============================================================================

@app.route('/api/advisor/advice', methods=['POST'])
@jwt_required()
def get_financial_advice():
    """Get AI financial advice using Gemini"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Use user's API key or fallback to app key
    api_key = user.gemini_api_key or GEMINI_API_KEY
    
    if not api_key:
        return jsonify({'error': 'Gemini API key not configured'}), 400
    
    try:
        # Configure with user's API key
        genai.configure(api_key=api_key)
        
        # Create context from user's financial data
        summary = Transaction.query.filter_by(user_id=user_id).all()
        
        total_income = sum(tx.amount for tx in summary if tx.type == 'income')
        total_expense = sum(tx.amount for tx in summary if tx.type == 'expense')
        net_balance = total_income - total_expense
        account_type = user.account_type
        
        # Build context message
        context = f"""
Anda adalah financial advisor yang ahli dalam manajemen keuangan.
User memiliki akun tipe: {account_type}
Statistik keuangan user:
- Total Pemasukan: Rp {total_income:,.0f}
- Total Pengeluaran: Rp {total_expense:,.0f}
- Saldo Bersih: Rp {net_balance:,.0f}

Berikan saran keuangan yang praktis, actionable, dan sesuai dengan situasi user.
Gunakan bahasa Indonesia yang jelas dan mudah dipahami.
        """
        
        prompt = f"{context}\n\nPertanyaan user: {question}"
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        advice = response.text
        
        return jsonify({
            'question': question,
            'advice': advice
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate advice',
            'details': str(e)
        }), 500


# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')


@app.route('/login')
def login_page():
    """Serve login page"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Serve registration page"""
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    """Serve dashboard page"""
    return render_template('dashboard.html')


@app.route('/transactions')
def transactions_page():
    """Serve transactions page"""
    return render_template('transactions.html')


@app.route('/advisor')
def advisor_page():
    """Serve AI advisor page"""
    return render_template('advisor.html')


@app.route('/settings')
def settings_page():
    """Serve settings page"""
    return render_template('settings.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# APP INITIALIZATION
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

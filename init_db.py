"""
Database initialization script with demo data
Run this before first launch to create tables and add demo user
"""

from app import app, db, User, Transaction
from datetime import datetime, timedelta

def init_db():
    """Initialize database with demo data"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created")

        # Check if demo user exists
        demo_user = User.query.filter_by(email='demo@example.com').first()
        if not demo_user:
            # Create demo user (personal account)
            demo_user = User(
                name='Demo User',
                email='demo@example.com',
                account_type='personal'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.flush()  # Get the ID
            print("✓ Demo user created (demo@example.com / demo123)")

            # Add sample transactions
            now = datetime.now()
            sample_transactions = [
                # Income
                Transaction(
                    user_id=demo_user.id,
                    date=(now - timedelta(days=30)).date(),
                    type='income',
                    category='Gaji',
                    amount=5000000,
                    description='Gaji bulan Mei'
                ),
                Transaction(
                    user_id=demo_user.id,
                    date=(now - timedelta(days=15)).date(),
                    type='income',
                    category='Freelance',
                    amount=1500000,
                    description='Project freelance'
                ),
                # Expenses
                Transaction(
                    user_id=demo_user.id,
                    date=(now - timedelta(days=28)).date(),
                    type='expense',
                    category='Makanan',
                    amount=150000,
                    description='Belanja groceries'
                ),
                Transaction(
                    user_id=demo_user.id,
                    date=(now - timedelta(days=25)).date(),
                    type='expense',
                    category='Transportasi',
                    amount=100000,
                    description='Isi bensin'
                ),
                Transaction(
                    user_id=demo_user.id,
                    date=(now - timedelta(days=20)).date(),
                    type='expense',
                    category='Tagihan',
                    amount=500000,
                    description='Listrik dan air'
                ),
                Transaction(
                    user_id=demo_user.id,
                    date=(now - timedelta(days=10)).date(),
                    type='expense',
                    category='Belanja',
                    amount=800000,
                    description='Baju dan aksesoris'
                ),
            ]

            db.session.add_all(sample_transactions)
            print("✓ Sample transactions added")

        # Create demo business user
        demo_business = User.query.filter_by(email='bisnis@example.com').first()
        if not demo_business:
            demo_business = User(
                name='Demo Business',
                email='bisnis@example.com',
                account_type='business',
                business_name='PT. Demo Indonesia',
                business_type='Perdagangan Umum'
            )
            demo_business.set_password('demo123')
            db.session.add(demo_business)
            db.session.flush()
            print("✓ Demo business user created (bisnis@example.com / demo123)")

            # Add business transactions
            business_transactions = [
                # Income
                Transaction(
                    user_id=demo_business.id,
                    date=(now - timedelta(days=30)).date(),
                    type='income',
                    category='Penjualan',
                    amount=25000000,
                    description='Penjualan barang dagangan'
                ),
                Transaction(
                    user_id=demo_business.id,
                    date=(now - timedelta(days=20)).date(),
                    type='income',
                    category='Jasa',
                    amount=5000000,
                    description='Konsultasi bisnis'
                ),
                # Expenses
                Transaction(
                    user_id=demo_business.id,
                    date=(now - timedelta(days=28)).date(),
                    type='expense',
                    category='Gaji Karyawan',
                    amount=10000000,
                    description='Gaji 5 karyawan'
                ),
                Transaction(
                    user_id=demo_business.id,
                    date=(now - timedelta(days=25)).date(),
                    type='expense',
                    category='Sewa',
                    amount=2000000,
                    description='Sewa kantor'
                ),
                Transaction(
                    user_id=demo_business.id,
                    date=(now - timedelta(days=15)).date(),
                    type='expense',
                    category='Bahan Baku',
                    amount=8000000,
                    description='Pembelian bahan baku'
                ),
                Transaction(
                    user_id=demo_business.id,
                    date=(now - timedelta(days=10)).date(),
                    type='expense',
                    category='Marketing',
                    amount=1500000,
                    description='Iklan media sosial'
                ),
            ]

            db.session.add_all(business_transactions)
            print("✓ Sample business transactions added")

        # Commit all changes
        db.session.commit()
        print("\n✅ Database initialization complete!")
        print("\nDemo Accounts:")
        print("  Personal: demo@example.com / demo123")
        print("  Business: bisnis@example.com / demo123")


if __name__ == '__main__':
    init_db()
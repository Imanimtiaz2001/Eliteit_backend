from app import app, db  # Import your app and db from your app.py
from models import Subscription
from datetime import datetime

def deactivate_expired_subscriptions():
    """Deactivate subscriptions that are expired."""
    today = datetime.today().date()
    
    # Get expired subscriptions
    expired_subs = Subscription.query.filter(Subscription.end_date < today, Subscription.is_active == True).all()

    for sub in expired_subs:
        sub.is_active = False  # Mark subscription as inactive
    db.session.commit()

    print(f"Deactivated {len(expired_subs)} expired subscriptions.")

if __name__ == '__main__':
    # Create application context to access the database
    with app.app_context():
        deactivate_expired_subscriptions()

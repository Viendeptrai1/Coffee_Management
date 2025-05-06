from app.database.db_config import get_db
from app.models.models import Order, MenuItem, order_item, Staff
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class StatsController:
    @staticmethod
    def get_revenue_by_date_range(start_date, end_date):
        db = get_db()
        try:
            orders = db.query(
                func.date(Order.order_time).label('date'),
                func.sum(Order.final_amount).label('revenue')
            ).filter(
                Order.order_time >= start_date,
                Order.order_time <= end_date,
                Order.status == "đã thanh toán"
            ).group_by(
                func.date(Order.order_time)
            ).all()
            
            # Convert to DataFrame for easier manipulation
            if orders:
                df = pd.DataFrame([(o.date, o.revenue) for o in orders], columns=['date', 'revenue'])
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                
                # Create a complete date range
                idx = pd.date_range(start=start_date, end=end_date)
                df = df.reindex(idx, fill_value=0)
                
                return df
            return pd.DataFrame(columns=['date', 'revenue'])
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return pd.DataFrame(columns=['date', 'revenue'])
        finally:
            db.close()
    
    @staticmethod
    def get_top_selling_items(start_date, end_date, limit=10):
        db = get_db()
        try:
            items = db.query(
                MenuItem.id,
                MenuItem.name,
                func.sum(order_item.c.quantity).label('quantity'),
                func.sum(MenuItem.price * order_item.c.quantity).label('revenue')
            ).join(
                order_item,
                MenuItem.id == order_item.c.menu_item_id
            ).join(
                Order,
                and_(
                    Order.id == order_item.c.order_id,
                    Order.order_time >= start_date,
                    Order.order_time <= end_date,
                    Order.status == "đã thanh toán"
                )
            ).group_by(
                MenuItem.id
            ).order_by(
                func.sum(order_item.c.quantity).desc()
            ).limit(limit).all()
            
            return items
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_hourly_distribution(days=30):
        start_date = datetime.now() - timedelta(days=days)
        
        db = get_db()
        try:
            hourly_data = db.query(
                extract('hour', Order.order_time).label('hour'),
                func.count(Order.id).label('count')
            ).filter(
                Order.order_time >= start_date,
                Order.status == "đã thanh toán"
            ).group_by(
                extract('hour', Order.order_time)
            ).all()
            
            # Convert to a more usable format
            hours = [0] * 24
            for data in hourly_data:
                hours[int(data.hour)] = data.count
            
            return hours
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return [0] * 24
        finally:
            db.close()
    
    @staticmethod
    def get_staff_performance(start_date, end_date):
        db = get_db()
        try:
            performance = db.query(
                Staff.id,
                Staff.name,
                func.count(Order.id).label('orders_count'),
                func.sum(Order.final_amount).label('total_revenue')
            ).join(
                Order,
                and_(
                    Staff.id == Order.staff_id,
                    Order.order_time >= start_date,
                    Order.order_time <= end_date,
                    Order.status == "đã thanh toán"
                )
            ).group_by(
                Staff.id
            ).all()
            
            return performance
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def predict_revenue(days_ahead=7):
        """Simple revenue prediction using linear regression"""
        # Get last 30 days data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        revenue_df = StatsController.get_revenue_by_date_range(start_date, end_date)
        
        if revenue_df.empty:
            return [0] * days_ahead
        
        # Prepare data for prediction
        X = np.array(range(len(revenue_df))).reshape(-1, 1)
        y = revenue_df['revenue'].values
        
        # Simple linear regression
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict future days
        X_pred = np.array(range(len(revenue_df), len(revenue_df) + days_ahead)).reshape(-1, 1)
        predictions = model.predict(X_pred)
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        return predictions.tolist()
    
    @staticmethod
    def get_category_distribution(start_date, end_date):
        db = get_db()
        try:
            category_data = db.query(
                MenuItem.category_id,
                func.sum(order_item.c.quantity).label('count')
            ).join(
                order_item,
                MenuItem.id == order_item.c.menu_item_id
            ).join(
                Order,
                and_(
                    Order.id == order_item.c.order_id,
                    Order.order_time >= start_date,
                    Order.order_time <= end_date,
                    Order.status == "đã thanh toán"
                )
            ).group_by(
                MenuItem.category_id
            ).all()
            
            return category_data
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close() 
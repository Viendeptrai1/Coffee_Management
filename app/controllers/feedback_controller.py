from app.database.db_config import get_db
from app.models.models import Feedback, Order, Customer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

class FeedbackController:
    @staticmethod
    def add_feedback(order_id, rating, comment=None, service_rating=None, 
                     food_rating=None, ambience_rating=None, customer_id=None):
        """Thêm đánh giá mới cho một đơn hàng"""
        db = get_db()
        try:
            # Kiểm tra order có tồn tại không
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False
            
            # Nếu đơn hàng có customer_id thì dùng, nếu không thì dùng customer_id được truyền vào
            if not customer_id and order.customer_id:
                customer_id = order.customer_id
            
            # Tạo đánh giá mới
            new_feedback = Feedback(
                order_id=order_id,
                customer_id=customer_id,
                rating=rating,
                comment=comment,
                service_rating=service_rating,
                food_rating=food_rating,
                ambience_rating=ambience_rating,
                created_at=datetime.now()
            )
            
            db.add(new_feedback)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_feedback_by_order(order_id):
        """Lấy đánh giá của một đơn hàng cụ thể"""
        db = get_db()
        try:
            feedback = db.query(Feedback).filter(Feedback.order_id == order_id).first()
            return feedback
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_feedbacks(limit=100, offset=0, sort_by="created_at", sort_dir="desc"):
        """Lấy tất cả đánh giá với phân trang"""
        db = get_db()
        try:
            query = db.query(Feedback).options(
                joinedload(Feedback.order),
                joinedload(Feedback.customer)
            )
            
            # Sắp xếp
            if sort_dir.lower() == "desc":
                query = query.order_by(desc(getattr(Feedback, sort_by)))
            else:
                query = query.order_by(getattr(Feedback, sort_by))
            
            # Phân trang
            feedbacks = query.offset(offset).limit(limit).all()
            return feedbacks
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_feedback_stats():
        """Lấy thống kê về đánh giá"""
        db = get_db()
        try:
            # Tổng số đánh giá
            total_count = db.query(func.count(Feedback.id)).scalar()
            
            # Đếm số lượng theo số sao
            rating_counts = db.query(
                Feedback.rating, 
                func.count(Feedback.id)
            ).group_by(Feedback.rating).all()
            
            # Tính trung bình
            avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0
            avg_service = db.query(func.avg(Feedback.service_rating)).scalar() or 0
            avg_food = db.query(func.avg(Feedback.food_rating)).scalar() or 0
            avg_ambience = db.query(func.avg(Feedback.ambience_rating)).scalar() or 0
            
            # Đánh giá gần đây (30 ngày)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_count = db.query(func.count(Feedback.id)).filter(
                Feedback.created_at >= thirty_days_ago
            ).scalar()
            
            # Đóng gói kết quả
            stats = {
                'total_count': total_count,
                'rating_distribution': {rating: count for rating, count in rating_counts},
                'avg_rating': round(float(avg_rating), 1),
                'avg_service': round(float(avg_service), 1),
                'avg_food': round(float(avg_food), 1),
                'avg_ambience': round(float(avg_ambience), 1),
                'recent_count': recent_count
            }
            
            return stats
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def delete_feedback(feedback_id):
        """Xóa một đánh giá"""
        db = get_db()
        try:
            feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
            if not feedback:
                return False
            
            db.delete(feedback)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close() 
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.session import Base


class OTPVerification(Base):
    """OTP verification table for password reset"""
    __tablename__ = 'otp_verifications'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    otp = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<OTPVerification(email='{self.email}', used={self.used})>"

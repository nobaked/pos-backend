from sqlalchemy import Column, Integer, String, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base



class Product(Base):
    """商品マスタテーブル"""
    __tablename__ = "products"
    
    PRD_ID = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='商品一意キー')
    CODE = Column(BigInteger, unique=True, nullable=False, index=True, comment='商品コード（バーコード）')
    NAME = Column(String(50), nullable=False, comment='商品名称')
    PRICE = Column(Integer, nullable=False, comment='商品単価')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())



class Transaction(Base):
    """取引テーブル"""
    __tablename__ = "transactions"
    
    TRD_ID = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='取引一意キー')
    DATETIME = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='取引日時')
    EMP_CD = Column(String(10), nullable=False, comment='レジ担当者コード')
    STORE_CD = Column(String(5), nullable=False, comment='店舗コード')
    POS_NO = Column(String(3), nullable=False, comment='POS機ID')
    TOTAL_AMT = Column(Integer, nullable=False, comment='合計金額（税込）')
    TTL_AMT_EX_TAX = Column(Integer, nullable=False, comment='合計金額（税抜）')
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # リレーションシップの追加
    details = relationship("TransactionDetail", back_populates="transaction", cascade="all, delete-orphan")



class TransactionDetail(Base):
    """取引明細テーブル"""
    __tablename__ = "transaction_details"
    
    TRD_ID = Column(
        Integer, 
        ForeignKey("transactions.TRD_ID", ondelete="CASCADE"), 
        primary_key=True,
        comment='取引一意キー'
    )
    DTL_ID = Column(Integer, primary_key=True, comment='取引明細一意キー')
    PRD_ID = Column(Integer, ForeignKey("products.PRD_ID"), nullable=False, comment='商品一意キー')
    PRD_CODE = Column(String(13), nullable=False, comment='商品コード')
    PRD_NAME = Column(String(50), nullable=False, comment='商品名称')
    PRD_PRICE = Column(Integer, nullable=False, comment='商品単価')
    TAX_CD = Column(String(2), nullable=False, comment='消費税区分')
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # リレーションシップの追加
    transaction = relationship("Transaction", back_populates="details")

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    """商品基本情報"""
    CODE: int = Field(..., description="商品コード（バーコード）")
    NAME: str = Field(..., max_length=50, description="商品名称")
    PRICE: int = Field(..., ge=0, description="商品単価")


class ProductResponse(ProductBase):
    """商品レスポンス"""
    PRD_ID: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseItem(BaseModel):
    """購入商品アイテム"""
    PRD_ID: int = Field(..., description="商品一意キー")
    PRD_CODE: str = Field(..., max_length=13, description="商品コード")
    PRD_NAME: str = Field(..., max_length=50, description="商品名称")
    PRD_PRICE: int = Field(..., ge=0, description="商品単価")
    quantity: int = Field(default=1, ge=1, description="数量")
    TAX_CD: str = Field(default="10", max_length=2, description="消費税区分")


class PurchaseRequest(BaseModel):
    """購入リクエスト"""
    items: list[PurchaseItem] = Field(..., min_length=1, description="購入商品リスト")
    EMP_CD: str = Field(..., max_length=10, description="レジ担当者コード")
    STORE_CD: str = Field(..., max_length=5, description="店舗コード")
    POS_NO: str = Field(..., max_length=3, description="POS機ID")


class PurchaseResponse(BaseModel):
    """購入レスポンス"""
    TRD_ID: int
    DATETIME: datetime
    TOTAL_AMT: int
    TTL_AMT_EX_TAX: int
    
    class Config:
        from_attributes = True


class TransactionDetailResponse(BaseModel):
    """取引明細レスポンス"""
    TRD_ID: int
    DTL_ID: int
    PRD_ID: int
    PRD_CODE: str
    PRD_NAME: str
    PRD_PRICE: int
    TAX_CD: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """取引レスポンス（詳細付き）"""
    TRD_ID: int
    DATETIME: datetime
    EMP_CD: str
    STORE_CD: str
    POS_NO: str
    TOTAL_AMT: int
    TTL_AMT_EX_TAX: int
    created_at: datetime
    
    class Config:
        from_attributes = True

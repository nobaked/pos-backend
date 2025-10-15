from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import math
from ..database import get_db
from ..models.pos import Product, Transaction, TransactionDetail
from ..schemas.pos import ProductResponse, PurchaseRequest, PurchaseResponse


router = APIRouter()



@router.get("/api/products/search/{barcode}", response_model=ProductResponse)
async def search_product(barcode: int, db: Session = Depends(get_db)):
    """
    バーコードで商品を検索
    
    Args:
        barcode: 商品のバーコード（13桁の数値）
        db: データベースセッション
        
    Returns:
        ProductResponse: 商品情報
        
    Raises:
        HTTPException: 商品が見つからない場合は404エラー
    """
    product = db.query(Product).filter(Product.CODE == barcode).first()
    
    if not product:
        raise HTTPException(
            status_code=404, 
            detail=f"Product with barcode {barcode} not found"
        )
    
    return product



@router.get("/api/products", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    商品一覧を取得
    
    Args:
        skip: スキップする件数
        limit: 取得する最大件数
        db: データベースセッション
        
    Returns:
        list[ProductResponse]: 商品リスト
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return products



@router.post("/api/purchase", response_model=PurchaseResponse)
async def create_purchase(
    purchase: PurchaseRequest, 
    db: Session = Depends(get_db)
):
    """
    購入処理を実行
    
    Args:
        purchase: 購入リクエスト
        db: データベースセッション
        
    Returns:
        PurchaseResponse: 取引情報
        
    Raises:
        HTTPException: 商品が見つからない、在庫不足などのエラー
    """
    try:
        # 商品の存在確認と税抜合計の計算
        ttl_amt_ex_tax = 0
        for item in purchase.items:
            product = db.query(Product).filter(Product.PRD_ID == item.PRD_ID).first()
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {item.PRD_ID} not found"
                )
            # 税抜価格 × 数量を加算
            ttl_amt_ex_tax += item.PRD_PRICE * item.quantity
        
        # 税込金額計算（消費税10%、小数点以下切り捨て）
        total_amt = math.floor(ttl_amt_ex_tax * 1.1)
        
        # 取引レコード作成
        transaction = Transaction(
            DATETIME=datetime.now(),
            EMP_CD=purchase.EMP_CD,
            STORE_CD=purchase.STORE_CD,
            POS_NO=purchase.POS_NO,
            TOTAL_AMT=total_amt,
            TTL_AMT_EX_TAX=ttl_amt_ex_tax
        )
        db.add(transaction)
        db.flush()  # TRD_IDを取得するためにflush
        
        # 取引明細レコード作成
        for idx, item in enumerate(purchase.items, start=1):
            detail = TransactionDetail(
                TRD_ID=transaction.TRD_ID,
                DTL_ID=idx,
                PRD_ID=item.PRD_ID,
                PRD_CODE=item.PRD_CODE,
                PRD_NAME=item.PRD_NAME,
                PRD_PRICE=item.PRD_PRICE,
                TAX_CD=item.TAX_CD
            )
            db.add(detail)
        
        db.commit()
        db.refresh(transaction)
        
        return PurchaseResponse(
            TRD_ID=transaction.TRD_ID,
            DATETIME=transaction.DATETIME,
            TOTAL_AMT=transaction.TOTAL_AMT,
            TTL_AMT_EX_TAX=transaction.TTL_AMT_EX_TAX
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

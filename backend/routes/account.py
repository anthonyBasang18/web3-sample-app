"""Account routes"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
from config import w3
from database import get_db
from models.account import AccountBalance
from models.transaction import Transaction
from services.blockchain import sync_transactions, get_account_balance

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/{address}")
async def account_balance(address: str, db: Session = Depends(get_db)):
    """Get ETH balance for a given address and store in database"""
    try:
        if not w3.is_address(address):
            raise HTTPException(status_code=400, detail="Invalid Ethereum address")
        
        balance_wei, balance_eth = get_account_balance(address)
        
        # Store/update in database
        account = db.query(AccountBalance).filter(AccountBalance.address == address).first()
        if account:
            account.balance_wei = str(balance_wei)
            account.balance_eth = Decimal(str(balance_eth))
        else:
            account = AccountBalance(
                address=address,
                balance_wei=str(balance_wei),
                balance_eth=Decimal(str(balance_eth))
            )
            db.add(account)
        db.commit()
        
        return {
            "address": address,
            "balanceWei": str(balance_wei),
            "balanceEth": str(balance_eth),
            "lastUpdated": account.last_updated.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch balance: {str(e)}")


@router.get("/{address}/txs")
async def account_transactions(address: str, db: Session = Depends(get_db), sync: bool = True):
    """Get last 10 transactions for a given address from database"""
    try:
        # Normalize address to checksum format
        address = w3.to_checksum_address(address)
        
        if not w3.is_address(address):
            raise HTTPException(status_code=400, detail="Invalid Ethereum address")
        
        # Get transactions from database first - check both from and to addresses
        db_transactions = db.query(Transaction).filter(
            (Transaction.from_address == address) | (Transaction.to_address == address)
        ).order_by(Transaction.block_number.desc()).limit(10).all()
        
        # Sync in background if requested (default: True)
        if sync:
            import asyncio
            from threading import Thread
            
            def background_sync():
                # Create new DB session for background thread
                from database import SessionLocal
                bg_db = SessionLocal()
                try:
                    sync_transactions(address, bg_db)
                finally:
                    bg_db.close()
            
            # Start background thread
            Thread(target=background_sync, daemon=True).start()
        
        return {
            "address": address,
            "transactions": [{
                "hash": tx.hash,
                "from": tx.from_address,
                "to": tx.to_address,
                "value": tx.value,
                "asset": tx.asset,
                "blockNum": hex(tx.block_number)
            } for tx in db_transactions],
            "count": len(db_transactions)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return {
            "address": address,
            "transactions": [],
            "count": 0
        }

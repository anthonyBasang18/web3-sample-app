"""Blockchain service for Web3 interactions"""
import os
from sqlalchemy.orm import Session
from config import w3
from models.transaction import Transaction

# Contract address for token detection
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "").lower()

# Function signatures (first 4 bytes of keccak256 hash)
PUBLIC_MINT_SIG = "0x40c10f19"  # publicMint(uint256)
TRANSFER_SIG = "0xa9059cbb"     # transfer(address,uint256)


def _is_address_involved(tx: dict, address: str) -> bool:
    """Check if address is involved in transaction (from or to)"""
    # Normalize all addresses to checksum format for comparison
    address_checksum = w3.to_checksum_address(address)
    tx_from = w3.to_checksum_address(tx['from']) if tx['from'] else None
    tx_to = w3.to_checksum_address(tx['to']) if tx['to'] else None
    
    is_from = tx_from == address_checksum
    is_to = tx_to == address_checksum
    return is_from or is_to


def _decode_token_transaction(tx: dict) -> tuple:
    """Decode token transaction to get operation type and amount"""
    if not tx['to'] or tx['to'].lower() != CONTRACT_ADDRESS:
        return None, None
    
    input_data = tx['input'].hex() if isinstance(tx['input'], bytes) else tx['input']
    
    # Check for publicMint
    if input_data.startswith(PUBLIC_MINT_SIG):
        amount_hex = input_data[10:74]  # Skip function sig (10 chars) + get uint256 (64 chars)
        amount = int(amount_hex, 16) if amount_hex else 0
        return "Mint", str(amount / 10**18)  # Convert from wei to tokens
    
    # Check for transfer
    if input_data.startswith(TRANSFER_SIG):
        amount_hex = input_data[74:138]  # Skip sig + address, get uint256
        amount = int(amount_hex, 16) if amount_hex else 0
        return "Transfer", str(amount / 10**18)
    
    return None, None


def _create_transaction_record(tx: dict, block_num: int) -> Transaction:
    """Create Transaction model from blockchain transaction"""
    # Try to decode as token transaction
    operation, token_amount = _decode_token_transaction(tx)
    
    # Normalize addresses to checksum format
    from_addr = w3.to_checksum_address(tx['from']) if tx['from'] else None
    to_addr = w3.to_checksum_address(tx['to']) if tx['to'] else "Contract Creation"
    
    if operation:
        return Transaction(
            hash=tx['hash'].hex(),
            from_address=from_addr,
            to_address=to_addr,
            value=token_amount,
            asset=operation,  # "Mint" or "Transfer"
            block_number=block_num
        )
    
    # Regular ETH transaction
    return Transaction(
        hash=tx['hash'].hex(),
        from_address=from_addr,
        to_address=to_addr,
        value=str(w3.from_wei(tx['value'], 'ether')),
        asset="ETH",
        block_number=block_num
    )


def sync_transactions(address: str, db: Session, block_range: int = 1000):
    """Scan recent blocks and sync transactions to database"""
    try:
        # Normalize address to checksum format
        address = w3.to_checksum_address(address)
        latest_block = w3.eth.block_number
        start_block = max(0, latest_block - block_range)
        
        print(f"Syncing transactions for {address} from block {start_block} to {latest_block}")
        
        for block_num in range(start_block, latest_block + 1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block.transactions:
                    # Skip if address not involved
                    if not _is_address_involved(tx, address):
                        continue
                    
                    # Skip if already exists
                    tx_hash = tx['hash'].hex()
                    if db.query(Transaction).filter(Transaction.hash == tx_hash).first():
                        continue
                    
                    # Add new transaction
                    new_tx = _create_transaction_record(tx, block_num)
                    db.add(new_tx)
                    print(f"Added transaction: {tx_hash}")
                    
            except Exception as e:
                # Skip failed blocks but log the error
                print(f"Failed to process block {block_num}: {str(e)}")
                continue
        
        db.commit()
        print(f"Sync completed for {address}")
        
    except Exception as e:
        print(f"Sync error for {address}: {str(e)}")
        db.rollback()


def get_account_balance(address: str):
    """Get ETH balance for an address"""
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    return balance_wei, balance_eth


def get_chain_metadata():
    """Get current gas price and block number"""
    latest_block = w3.eth.get_block('latest')
    gas_price = w3.eth.gas_price
    
    return {
        "blockNumber": latest_block.number,
        "gasPrice": str(gas_price),
        "gasPriceGwei": w3.from_wei(gas_price, 'gwei'),
        "timestamp": latest_block.timestamp
    }

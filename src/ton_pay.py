"""
TON blockchain payment processing
"""
import os
import logging
import uuid
from typing import Dict

logger = logging.getLogger(__name__)

# TON wallet configuration
TON_WALLET_ADDRESS = os.getenv("TON_WALLET_ADDRESS", "")
PAYMENT_AMOUNT = float(os.getenv("PAYMENT_AMOUNT", "1.0"))  # Default 1 TON

# In-memory storage for demo (use database in production)
payments_db = {}


def create_payment(user_id: int) -> Dict[str, str]:
    """
    Create a new payment request
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        dict: Payment data including payment_id, amount, and payment_url
    """
    payment_id = str(uuid.uuid4())
    
    # Create TON payment URL
    # Format: ton://transfer/<address>?amount=<amount>&text=<comment>
    payment_url = (
        f"ton://transfer/{TON_WALLET_ADDRESS}"
        f"?amount={int(PAYMENT_AMOUNT * 1e9)}"  # Convert TON to nanotons
        f"&text=cat_gen_{payment_id}"
    )
    
    # Store payment info
    payments_db[payment_id] = {
        "user_id": user_id,
        "amount": PAYMENT_AMOUNT,
        "status": "pending",
        "payment_url": payment_url
    }
    
    logger.info(f"Created payment {payment_id} for user {user_id}")
    
    return {
        "payment_id": payment_id,
        "amount": PAYMENT_AMOUNT,
        "payment_url": payment_url
    }


def check_payment_status(payment_id: str) -> bool:
    """
    Check if payment has been confirmed
    
    Args:
        payment_id: Payment identifier
        
    Returns:
        bool: True if payment is confirmed, False otherwise
    """
    if payment_id not in payments_db:
        logger.warning(f"Payment {payment_id} not found")
        return False
    
    payment = payments_db[payment_id]
    
    # In a real implementation, you would:
    # 1. Query TON blockchain API to check for incoming transaction
    # 2. Verify the transaction amount and comment match
    # 3. Update payment status in database
    
    # For demo purposes, we'll simulate payment confirmation
    # In production, integrate with TON API or webhook
    
    # Simulate: Mark first check as confirmed (for demo)
    if payment["status"] == "pending":
        payment["status"] = "confirmed"
        logger.info(f"Payment {payment_id} confirmed")
        return True
    
    return payment["status"] == "confirmed"


def get_payment_info(payment_id: str) -> Dict:
    """
    Get payment information
    
    Args:
        payment_id: Payment identifier
        
    Returns:
        dict: Payment information or None if not found
    """
    return payments_db.get(payment_id)


def verify_ton_transaction(transaction_hash: str, expected_amount: float, expected_comment: str) -> bool:
    """
    Verify a TON blockchain transaction
    
    Args:
        transaction_hash: Transaction hash to verify
        expected_amount: Expected payment amount in TON
        expected_comment: Expected transaction comment
        
    Returns:
        bool: True if transaction is valid, False otherwise
    """
    # In production, implement actual blockchain verification:
    # 1. Use TON API to fetch transaction details
    # 2. Verify sender, receiver, amount, and comment
    # 3. Ensure transaction is confirmed
    
    logger.info(f"Verifying transaction {transaction_hash}")
    
    # Placeholder for demo
    return True

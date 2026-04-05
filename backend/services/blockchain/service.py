"""
UUHAKIX Blockchain Service — Polygon Smart Contract Interaction
"""

from typing import List, Dict, Any, Optional
from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract
from core.config import settings
import structlog
import json

logger = structlog.get_logger()

TRANSPARENCY_REGISTRY_ABI = json.load(open("blockchain/contracts/TransparencyRegistry.json", "r"))


class BlockchainService:
    """Interact with the TransparencyRegistry smart contract on Polygon."""

    def __init__(self):
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.polygon_rpc_url))
        self.contract: Optional[AsyncContract] = None
        self.account = None

    async def initialize(self):
        """Initialize contract connection."""
        self.account = self.w3.eth.account.from_key(settings.blockchain_private_key)
        if settings.contract_address:
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(settings.contract_address),
                abi=TRANSPARENCY_REGISTRY_ABI,
            )
            logger.info("blockchain_initialized", address=settings.contract_address)

    async def record_hash(
        self,
        data_hash: str,
        data_type: str,
        reference_id: str,
    ) -> Dict[str, Any]:
        """Record a single data hash on-chain."""
        if not self.contract:
            raise RuntimeError("Blockchain not initialized")

        nonce = await self.w3.eth.get_transaction_count(self.account.address)
        tx = await self.contract.functions.recordHash(
            bytes.fromhex(data_hash),
            data_type,
            reference_id,
        ).build_transaction({
            "from": self.account.address,
            "nonce": nonce,
            "gasPrice": await self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info("hash_recorded", data_type=data_type, tx_hash=tx_hash.hex())

        return {
            "tx_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "status": receipt.status,
            "data_hash": data_hash,
            "data_type": data_type,
            "reference_id": reference_id,
        }

    async def record_batch(
        self,
        batch_id: str,
        hashes: List[str],
        data_type: str,
    ) -> Dict[str, Any]:
        """Record a batch of hashes for gas efficiency."""
        if not self.contract:
            raise RuntimeError("Blockchain not initialized")

        nonce = await self.w3.eth.get_transaction_count(self.account.address)
        tx = await self.contract.functions.recordBatch(
            batch_id,
            [bytes.fromhex(h) for h in hashes],
            data_type,
        ).build_transaction({
            "from": self.account.address,
            "nonce": nonce,
            "gasPrice": await self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info("batch_recorded", batch_id=batch_id, count=len(hashes), tx_hash=tx_hash.hex())

        return {
            "tx_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "status": receipt.status,
            "hash_count": len(hashes),
            "batch_id": batch_id,
        }

    async def verify_hash(self, data_hash: str) -> Dict[str, Any]:
        """Verify if a data hash exists on-chain."""
        if not self.contract:
            raise RuntimeError("Blockchain not initialized")

        exists = await self.contract.functions.verifyHash(bytes.fromhex(data_hash)).call()

        if exists:
            record = await self.contract.functions.getRecord(bytes.fromhex(data_hash)).call()
            return {
                "exists": True,
                "submitter": record[0],
                "timestamp": record[1],
                "data_type": record[2],
                "reference_id": record[3],
            }

        return {"exists": False, "data_hash": data_hash}


blockchain_service = BlockchainService()

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * UUHAKIX Transparency Registry
 * Stores hashes of verified government data + election results on Polygon.
 * Immutable, publicly verifiable, cannot be tampered.
 *
 * Deployment: Polygon Amoy (testnet) → Polygon Mainnet
 */

contract TransparencyRegistry {
    struct DataRecord {
        bytes32 dataHash;       // SHA-256 hash of the data
        address submitter;      // LEDGER agent wallet
        uint256 timestamp;      // When it was recorded
        string dataType;        // "election" | "transaction" | "budget" | "procurement"
        string referenceId;     // External reference (e.g., submission_id)
        bool exists;            // Existence flag for mapping lookup
    }

    struct BatchRecord {
        bytes32[] hashes;
        string dataType;
        uint256 timestamp;
        uint256 hashCount;
        bool exists;
    }

    // ── State ───────────────────────────────────────────────
    mapping(bytes32 => DataRecord) public records;
    mapping(string => BatchRecord) public batches;
    mapping(address => bool) public authorizedSubmitters;

    address public owner;
    uint256 public totalRecords;
    uint256 public totalBatches;

    // ── Events ──────────────────────────────────────────────
    event DataRecorded(
        bytes32 indexed hash,
        string dataType,
        string referenceId,
        uint256 timestamp,
        address submitter
    );

    event BatchRecorded(
        string indexed batchId,
        uint256 hashCount,
        string dataType,
        uint256 timestamp
    );

    event SubmitterAuthorized(address indexed submitter, bool authorized);

    // ── Modifiers ───────────────────────────────────────────
    modifier onlyOwner() {
        require(msg.sender == owner, "UUHAKIX: not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedSubmitters[msg.sender], "UUHAKIX: not authorized");
        _;
    }

    // ── Constructor ─────────────────────────────────────────
    constructor() {
        owner = msg.sender;
        authorizedSubmitters[msg.sender] = true;
    }

    // ── Single Record ───────────────────────────────────────
    /**
     * Record a single data hash on-chain.
     * @param dataHash SHA-256 hash of the verified data
     * @param dataType Type: "election", "transaction", "budget", "procurement"
     * @param referenceId External reference for lookup
     */
    function recordHash(
        bytes32 dataHash,
        string calldata dataType,
        string calldata referenceId
    ) external onlyAuthorized {
        require(!records[dataHash].exists, "UUHAKIX: hash already recorded");

        records[dataHash] = DataRecord({
            dataHash: dataHash,
            submitter: msg.sender,
            timestamp: block.timestamp,
            dataType: dataType,
            referenceId: referenceId,
            exists: true
        });

        totalRecords++;

        emit DataRecorded(dataHash, dataType, referenceId, block.timestamp, msg.sender);
    }

    // ── Batch Record ────────────────────────────────────────
    /**
     * Record a batch of hashes at once for gas efficiency.
     * LEDGER agent batches submissions.
     * @param batchId Unique batch identifier
     * @param hashes Array of data hashes
     * @param dataType Type of data in this batch
     */
    function recordBatch(
        string calldata batchId,
        bytes32[] calldata hashes,
        string calldata dataType
    ) external onlyAuthorized {
        require(!batches[batchId].exists, "UUHAKIX: batch already recorded");
        require(hashes.length > 0, "UUHAKIX: empty batch");

        // Record individual hashes
        for (uint256 i = 0; i < hashes.length; i++) {
            if (!records[hashes[i]].exists) {
                records[hashes[i]] = DataRecord({
                    dataHash: hashes[i],
                    submitter: msg.sender,
                    timestamp: block.timestamp,
                    dataType: dataType,
                    referenceId: string(abi.encodePacked(batchId, "-", uint2str(i))),
                    exists: true
                });
                totalRecords++;
            }
        }

        // Record batch metadata
        batches[batchId] = BatchRecord({
            hashes: hashes,
            dataType: dataType,
            timestamp: block.timestamp,
            hashCount: hashes.length,
            exists: true
        });

        totalBatches++;

        emit BatchRecorded(batchId, hashes.length, dataType, block.timestamp);
    }

    // ── Authorization ───────────────────────────────────────
    function authorizeSubmitter(address submitter, bool authorized) external onlyOwner {
        authorizedSubmitters[submitter] = authorized;
        emit SubmitterAuthorized(submitter, authorized);
    }

    // ── Verification ────────────────────────────────────────
    /**
     * Verify if a data hash exists on-chain.
     * Citizens can use this to verify government data hasn't been tampered.
     */
    function verifyHash(bytes32 dataHash) external view returns (bool) {
        return records[dataHash].exists;
    }

    /**
     * Get details of a recorded hash.
     */
    function getRecord(bytes32 dataHash) external view returns (
        address submitter,
        uint256 timestamp,
        string memory dataType,
        string memory referenceId
    ) {
        require(records[dataHash].exists, "UUHAKIX: hash not found");
        DataRecord storage record = records[dataHash];
        return (record.submitter, record.timestamp, record.dataType, record.referenceId);
    }

    /**
     * Get batch details.
     */
    function getBatch(string calldata batchId) external view returns (
        string memory dataType,
        uint256 timestamp,
        uint256 hashCount
    ) {
        require(batches[batchId].exists, "UUHAKIX: batch not found");
        BatchRecord storage batch = batches[batchId];
        return (batch.dataType, batch.timestamp, batch.hashCount);
    }

    // ── Stats ───────────────────────────────────────────────
    function getStats() external view returns (
        uint256 _totalRecords,
        uint256 _totalBatches
    ) {
        return (totalRecords, totalBatches);
    }

    // ── Helpers ─────────────────────────────────────────────
    function uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) return "0";
        uint256 j = _i;
        uint256 length;
        while (j != 0) {
            length++;
            j /= 10;
        }
        bytes memory bstr = new bytes(length);
        uint256 k = length;
        j = _i;
        while (j != 0) {
            bstr[--k] = bytes1(uint8(48 + (j % 10)));
            j /= 10;
        }
        return string(bstr);
    }

    // ── Ownership Transfer ──────────────────────────────────
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "UUHAKIX: zero address");
        owner = newOwner;
    }
}

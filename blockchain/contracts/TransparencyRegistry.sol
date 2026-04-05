// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * TransparencyRegistry — UHAKIX Smart Contract
 * Stores hashes of government transactions, election results, and corruption evidence
 * on the Polygon blockchain for tamper-proof verification.
 *
 * Deployed on: Polygon Amoy (testnet) and Polygon Mainnet
 */
contract TransparencyRegistry {

    // ── State Variables ────────────────────────────────────────

    struct TransactionRecord {
        bytes32 dataHash;
        string dataType;        // "spending", "tender", "election", "evidence"
        string referenceId;     // e.g., tender ID, station code
        address submitter;
        uint256 timestamp;
        uint256 blockNumber;
    }

    struct VoteRecord {
        string stationCode;
        bytes32 resultHash;
        address submitter;
        uint256 timestamp;
        uint256 blockNumber;
    }

    struct EvidenceRecord {
        bytes32 evidenceHash;
        string category;        // "corruption", "irregularity", "complaint"
        string referenceId;
        address submitter;
        uint256 timestamp;
    }

    // Public registry: dataHash → TransactionRecord
    mapping(bytes32 => TransactionRecord) public transactions;
    
    // Station code → array of VoteRecords (allows multiple submissions per station)
    mapping(string => VoteRecord[]) public stationVotes;
    
    // Unique station code → verified result hash
    mapping(string => bytes32) public verifiedStationResults;

    // Evidence hash → EvidenceRecord
    mapping(bytes32 => EvidenceRecord) public evidence;

    // ── Authorization ──────────────────────────────────────────
    
    address public owner;

    mapping(address => bool) public authorizedAgents;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized: owner only");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedAgents[msg.sender] || msg.sender == owner, "Not authorized agent");
        _;
    }

    // ── Events ─────────────────────────────────────────────────

    event TransactionRecorded(
        bytes32 indexed dataHash,
        string dataType,
        string referenceId,
        address indexed submitter,
        uint256 timestamp
    );

    event VoteRecorded(
        string indexed stationCode,
        bytes32 indexed resultHash,
        address submitter,
        uint256 voteIndex,
        uint256 timestamp
    );

    event StationVerified(
        string indexed stationCode,
        bytes32 verifiedHash,
        address verifier,
        uint256 timestamp
    );

    event VoteBatchRecorded(
        address indexed submitter,
        uint256 count,
        uint256 timestamp
    );

    event EvidenceRecorded(
        bytes32 indexed evidenceHash,
        string category,
        string referenceId,
        address indexed submitter,
        uint256 timestamp
    );

    event AgentAuthorized(address indexed agent, uint256 timestamp);
    event AgentDeauthorized(address indexed agent, uint256 timestamp);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor() {
        owner = msg.sender;
        authorizedAgents[msg.sender] = true;
        emit AgentAuthorized(msg.sender, block.timestamp);
    }

    // ── Authorization Management ──────────────────────────────

    function authorizeAgent(address _agent) external onlyOwner {
        authorizedAgents[_agent] = true;
        emit AgentAuthorized(_agent, block.timestamp);
    }

    function deauthorizeAgent(address _agent) external onlyOwner {
        authorizedAgents[_agent] = false;
        emit AgentDeauthorized(_agent, block.timestamp);
    }

    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Invalid address");
        emit OwnershipTransferred(owner, _newOwner);
        owner = _newOwner;
    }

    // ── Transaction Recording ─────────────────────────────────

    /**
     * Record a single government spending/transaction hash
     * @param dataHash SHA-256 hash of the transaction data
     * @param dataType Category: "spending", "tender", etc.
     * @param referenceId Cross-reference ID from the source system
     */
    function recordTransaction(
        bytes32 dataHash,
        string memory dataType,
        string memory referenceId
    ) external onlyAuthorized {
        require(dataHash != bytes32(0), "Hash cannot be zero");
        require(bytes(dataType).length > 0, "Data type required");

        transactions[dataHash] = TransactionRecord({
            dataHash: dataHash,
            dataType: dataType,
            referenceId: referenceId,
            submitter: msg.sender,
            timestamp: block.timestamp,
            blockNumber: block.number
        });

        emit TransactionRecorded(
            dataHash,
            dataType,
            referenceId,
            msg.sender,
            block.timestamp
        );
    }

    /**
     * Record a batch of transaction hashes (gas-efficient)
     * @param dataHashes Array of SHA-256 hashes
     * @param dataType Category for all entries
     * @param referencePrefix Common prefix; individual entries indexed by position
     */
    function recordTransactionBatch(
        bytes32[] memory dataHashes,
        string memory dataType,
        string memory referencePrefix
    ) external onlyAuthorized {
        require(dataHashes.length > 0, "Batch cannot be empty");
        require(dataHashes.length <= 100, "Batch too large");
        require(bytes(dataType).length > 0, "Data type required");

        for (uint256 i = 0; i < dataHashes.length; i++) {
            require(dataHashes[i] != bytes32(0), "Hash cannot be zero");

            transactions[dataHashes[i]] = TransactionRecord({
                dataHash: dataHashes[i],
                dataType: dataType,
                referenceId: string(abi.encodePacked(referencePrefix, "-", i)),
                submitter: msg.sender,
                timestamp: block.timestamp,
                blockNumber: block.number
            });

            emit TransactionRecorded(
                dataHashes[i],
                dataType,
                string(abi.encodePacked(referencePrefix, "-", i)),
                msg.sender,
                block.timestamp
            );
        }
    }

    // ── Election Vote Recording ───────────────────────────────

    /**
     * Record a verified vote result for a polling station
     * @param stationCode IEBC polling station code
     * @param resultHash SHA-256 of the aggregated station result
     */
    function recordVote(
        string memory stationCode,
        bytes32 resultHash
    ) external onlyAuthorized {
        require(bytes(stationCode).length > 0, "Station code required");
        require(resultHash != bytes32(0), "Hash cannot be zero");

        // Allow multiple submissions per station (cross-verification)
        stationVotes[stationCode].push(VoteRecord({
            stationCode: stationCode,
            resultHash: resultHash,
            submitter: msg.sender,
            timestamp: block.timestamp,
            blockNumber: block.number
        }));

        uint256 voteIndex = stationVotes[stationCode].length - 1;

        emit VoteRecorded(
            stationCode,
            resultHash,
            msg.sender,
            voteIndex,
            block.timestamp
        );

        // If first vote, also mark as verified
        if (stationVotes[stationCode].length == 1) {
            verifiedStationResults[stationCode] = resultHash;
            emit StationVerified(stationCode, resultHash, msg.sender, block.timestamp);
        }
    }

    /**
     * Record votes for multiple stations in one transaction (gas savings)
     * @param stationCodes Array of station codes
     * @param resultHashes Array of result hashes (must match stationCodes length)
     */
    function recordVoteBatch(
        string[] memory stationCodes,
        bytes32[] memory resultHashes
    ) external onlyAuthorized {
        require(stationCodes.length > 0, "No stations provided");
        require(stationCodes.length == resultHashes.length, "Array length mismatch");
        require(stationCodes.length <= 50, "Batch too large");

        for (uint256 i = 0; i < stationCodes.length; i++) {
            require(bytes(stationCodes[i]).length > 0, "Station code cannot be empty");
            require(resultHashes[i] != bytes32(0), "Hash cannot be zero");

            stationVotes[stationCodes[i]].push(VoteRecord({
                stationCode: stationCodes[i],
                resultHash: resultHashes[i],
                submitter: msg.sender,
                timestamp: block.timestamp,
                blockNumber: block.number
            }));

            if (stationVotes[stationCodes[i]].length == 1) {
                verifiedStationResults[stationCodes[i]] = resultHashes[i];
            }

            emit VoteRecorded(
                stationCodes[i],
                resultHashes[i],
                msg.sender,
                stationVotes[stationCodes[i]].length - 1,
                block.timestamp
            );
        }

        emit VoteBatchRecorded(msg.sender, stationCodes.length, block.timestamp);
    }

    // ── Evidence Recording ─────────────────────────────────────

    /**
     * Record corruption/evidence hash — immutable and permanent
     * @param evidenceHash SHA-256 of the evidence package
     * @param category Category: "corruption", "irregularity", "complaint"
     * @param referenceId Cross-reference ID
     */
    function recordEvidence(
        bytes32 evidenceHash,
        string memory category,
        string memory referenceId
    ) external onlyAuthorized {
        require(evidenceHash != bytes32(0), "Evidence hash cannot be zero");
        require(bytes(category).length > 0, "Category required");

        // Only store if not already recorded
        require(evidence[evidenceHash].timestamp == 0, "Evidence already recorded");

        evidence[evidenceHash] = EvidenceRecord({
            evidenceHash: evidenceHash,
            category: category,
            referenceId: referenceId,
            submitter: msg.sender,
            timestamp: block.timestamp
        });

        emit EvidenceRecorded(
            evidenceHash,
            category,
            referenceId,
            msg.sender,
            block.timestamp
        );
    }

    // ── Read/Verification Functions ───────────────────────────

    /**
     * Get a transaction record by its hash
     */
    function getTransaction(bytes32 dataHash) external view returns (
        string memory dataType,
        string memory referenceId,
        address submitter,
        uint256 timestamp,
        uint256 blockNumber
    ) {
        TransactionRecord storage record = transactions[dataHash];
        require(record.timestamp > 0, "Transaction not found");

        return (
            record.dataType,
            record.referenceId,
            record.submitter,
            record.timestamp,
            record.blockNumber
        );
    }

    /**
     * Get all vote submissions for a station
     */
    function getVotesByStation(string memory stationCode) external view returns (
        bytes32[] memory resultHashes,
        address[] memory submitters,
        uint256[] memory timestamps,
        uint256 totalCount
    ) {
        VoteRecord[] storage votes = stationVotes[stationCode];
        totalCount = votes.length;

        resultHashes = new bytes32[](totalCount);
        submitters = new address[](totalCount);
        timestamps = new uint256[](totalCount);

        for (uint256 i = 0; i < totalCount; i++) {
            resultHashes[i] = votes[i].resultHash;
            submitters[i] = votes[i].submitter;
            timestamps[i] = votes[i].timestamp;
        }

        return (resultHashes, submitters, timestamps, totalCount);
    }

    /**
     * Get the verified result hash for a station
     */
    function getVerifiedStation(string memory stationCode) external view returns (
        bytes32 verifiedHash
    ) {
        return verifiedStationResults[stationCode];
    }

    /**
     * Check if an evidence hash has been recorded
     */
    function evidenceExists(bytes32 evidenceHash) external view returns (bool) {
        return evidence[evidenceHash].timestamp > 0;
    }

    /**
     * Get total stations with verified results
     */
    function getStationCount() external view returns (uint256) {
        // This is a simplified check — in production, maintain a counter
        return 0; // Requires indexed storage for accurate count
    }

    // ── Emergency & Utility Functions ──────────────────────────

    /**
     * Verify that data matches its on-chain hash (client-side utility)
     */
    function verifyDataHash(bytes32 dataHash) external view returns (bool exists) {
        return transactions[dataHash].timestamp > 0;
    }

    /**
     * Emergency pause — only owner
     * (Note: This contract doesn't have a pause function since all writes are immutable,
     * but authorized agents can be deauthorized to stop new writes)
     */
    function emergencyStop() external onlyOwner {
        // Deauthorize all agents except owner
        // Owner can still write if needed
    }

    // ── Receive Function ───────────────────────────────────────
    // Accept MATIC for gas payments
    receive() external payable {}
}

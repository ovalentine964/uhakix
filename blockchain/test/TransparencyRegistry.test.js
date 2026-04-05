const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TransparencyRegistry", function () {
  let registry;
  let owner;
  let agent1;
  let agent2;
  let unauthorized;

  const DATA_HASH = ethers.keccak256(ethers.toUtf8Bytes("test-data-001"));
  const DATA_HASH_2 = ethers.keccak256(ethers.toUtf8Bytes("test-data-002"));
  const STATION_CODE = "KE-071-042";

  beforeEach(async function () {
    [owner, agent1, agent2, unauthorized] = await ethers.getSigners();
    const Contract = await ethers.getContractFactory("TransparencyRegistry");
    registry = await Contract.deploy();
    await registry.waitForDeployment();

    // Authorize agents
    await registry.connect(owner).authorizeAgent(await agent1.getAddress());
    await registry.connect(owner).authorizeAgent(await agent2.getAddress());
  });

  it("1. Should deploy with owner as authorized agent", async function () {
    expect(await registry.owner()).to.equal(await owner.getAddress());
    expect(await registry.authorizedAgents(await owner.getAddress())).to.be.true;
  });

  it("2. Should allow authorized agent to record a transaction", async function () {
    const refId = "IFMIS-2024-0001";
    const tx = await registry
      .connect(agent1)
      .recordTransaction(DATA_HASH, "spending", refId);

    const receipt = await tx.wait();
    const event = receipt.logs.find(
      (l) => l.fragment && l.fragment.name === "TransactionRecorded"
    );
    expect(event).to.not.be.undefined;

    const record = await registry.getTransaction(DATA_HASH);
    expect(record.dataType).to.equal("spending");
    expect(record.referenceId).to.equal(refId);
    expect(record.submitter).to.equal(await agent1.getAddress());
    expect(record.timestamp).to.be.greaterThan(0);
  });

  it("3. Should reject unauthorized user recording transactions", async function () {
    await expect(
      registry.connect(unauthorized).recordTransaction(DATA_HASH, "spending", "ref")
    ).to.be.revertedWith("Not authorized agent");
  });

  it("4. Should record election votes and return all submissions", async function () {
    const resultHash1 = ethers.keccak256(ethers.toUtf8Bytes("result-v1"));
    const resultHash2 = ethers.keccak256(ethers.toUtf8Bytes("result-v2"));

    await registry.connect(agent1).recordVote(STATION_CODE, resultHash1);
    await registry.connect(agent2).recordVote(STATION_CODE, resultHash2);

    const [hashes, submitters, timestamps, totalCount] =
      await registry.getVotesByStation(STATION_CODE);

    expect(totalCount).to.equal(2);
    expect(hashes[0]).to.equal(resultHash1);
    expect(hashes[1]).to.equal(resultHash2);
    expect(submitters[0]).to.equal(await agent1.getAddress());
    expect(submitters[1]).to.equal(await agent2.getAddress());
  });

  it("5. Should record evidence and verify existence", async function () {
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("evidence-001"));

    await registry
      .connect(agent1)
      .recordEvidence(evidenceHash, "irregularity", "CASE-001");

    expect(await registry.evidenceExists(evidenceHash)).to.be.true;

    await expect(
      registry.connect(agent1).recordEvidence(evidenceHash, "irregularity", "CASE-001")
    ).to.be.revertedWith("Evidence already recorded");
  });

  it("6. Should record batch transactions (gas-efficient)", async function () {
    const hashes = [
      ethers.keccak256(ethers.toUtf8Bytes("batch-1")),
      ethers.keccak256(ethers.toUtf8Bytes("batch-2")),
      ethers.keccak256(ethers.toUtf8Bytes("batch-3")),
    ];

    const tx = await registry
      .connect(agent1)
      .recordTransactionBatch(hashes, "tender", "TENDER-BATCH");
    await tx.wait();

    for (const h of hashes) {
      const record = await registry.getTransaction(h);
      expect(record.dataType).to.equal("tender");
    }
  });

  it("7. Should record vote batch for multiple stations", async function () {
    const stations = ["STN-001", "STN-002", "STN-003"];
    const hashes = [
      ethers.keccak256(ethers.toUtf8Bytes("vote-1")),
      ethers.keccak256(ethers.toUtf8Bytes("vote-2")),
      ethers.keccak256(ethers.toUtf8Bytes("vote-3")),
    ];

    await registry.connect(agent1).recordVoteBatch(stations, hashes);

    // First submission sets verified result
    for (let i = 0; i < stations.length; i++) {
      const v = await registry.getVerifiedStation(stations[i]);
      expect(v).to.equal(hashes[i]);
    }
  });

  it("8. Should allow owner to deauthorize an agent", async function () {
    await registry.connect(owner).deauthorizeAgent(await agent1.getAddress());
    expect(await registry.authorizedAgents(await agent1.getAddress())).to.be.false;

    await expect(
      registry.connect(agent1).recordTransaction(DATA_HASH, "test", "ref")
    ).to.be.revertedWith("Not authorized agent");
  });

  it("9. Should reject zero hash", async function () {
    await expect(
      registry.connect(agent1).recordTransaction(ethers.ZeroHash, "spending", "x")
    ).to.be.revertedWith("Hash cannot be zero");

    await expect(
      registry.connect(agent1).recordVote(STATION_CODE, ethers.ZeroHash)
    ).to.be.revertedWith("Hash cannot be zero");
  });

  it("10. Should verify data existence via verifyDataHash", async function () {
    await registry.connect(agent1).recordTransaction(DATA_HASH, "spending", "ref");
    expect(await registry.verifyDataHash(DATA_HASH)).to.be.true;
    expect(await registry.verifyDataHash(DATA_HASH_2)).to.be.false;
  });
});

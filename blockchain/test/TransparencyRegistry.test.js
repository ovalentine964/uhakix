const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TransparencyRegistry", function () {
  let registry;
  let owner;
  let ledgerAgent;
  let unauthorizedUser;

  const dataHash = ethers.keccak256(ethers.toUtf88Bytes("test data"));
  const batchId = "batch-001";

  beforeEach(async function () {
    [owner, ledgerAgent, unauthorizedUser] = await ethers.getSigners();

    const TransparencyRegistry = await ethers.getContractFactory("TransparencyRegistry");
    registry = await TransparencyRegistry.deploy();
    await registry.waitForDeployment();

    // Authorize LEDGER agent
    await registry.authorizeSubmitter(ledgerAgent.address, true);
  });

  it("should deploy with owner as authorized submitter", async function () {
    expect(await registry.owner()).to.equal(owner.address);
    expect(await registry.authorizedSubmitters(owner.address)).to.be.true;
  });

  it("should record a single hash", async function () {
    const tx = await registry.connect(ledgerAgent).recordHash(
      dataHash,
      "election",
      "station-001"
    );
    const receipt = await tx.wait();

    expect(await registry.verifyHash(dataHash)).to.be.true;

    const record = await registry.getRecord(dataHash);
    expect(record.dataType).to.equal("election");
    expect(record.referenceId).to.equal("station-001");
  });

  it("should emit DataRecorded event", async function () {
    await expect(
      registry.connect(ledgerAgent).recordHash(dataHash, "election", "station-001")
    ).to.emit(registry, "DataRecorded")
      .withArgs(dataHash, "election", "station-001", await ethers.provider.getBlock("latest").then(b => b.timestamp + 1), ledgerAgent.address);
  });

  it("should reject duplicate hashes", async function () {
    await registry.connect(ledgerAgent).recordHash(dataHash, "election", "station-001");
    await expect(
      registry.connect(ledgerAgent).recordHash(dataHash, "election", "station-001-dup")
    ).to.be.revertedWith("UUUHAKIX: hash already recorded");
  });

  it("should reject unauthorized submitters", async function () {
    await expect(
      registry.connect(unauthorizedUser).recordHash(dataHash, "election", "station-001")
    ).to.be.revertedWith("UUUHAKIX: not authorized");
  });

  it("should record a batch of hashes", async function () {
    const hashes = [
      ethers.keccak256(ethers.toUtf8Bytes("data1")),
      ethers.keccak256(ethers.toUtf8Bytes("data2")),
      ethers.keccak256(ethers.toUtf8Bytes("data3")),
    ];

    const tx = await registry.connect(ledgerAgent).recordBatch(batchId, hashes, "election");
    await tx.wait();

    // All hashes should be verifiable
    for (const hash of hashes) {
      expect(await registry.verifyHash(hash)).to.be.true;
    }

    const batch = await registry.getBatch(batchId);
    expect(batch.hashCount).to.equal(3);
    expect(batch.dataType).to.equal("election");
  });

  it("should reject duplicate batch IDs", async function () {
    const hashes = [ethers.keccak256(ethers.toUtf8Bytes("data1"))];
    await registry.connect(ledgerAgent).recordBatch(batchId, hashes, "election");
    await expect(
      registry.connect(ledgerAgent).recordBatch(batchId, hashes, "election")
    ).to.be.revertedWith("UUUHAKIX: batch already recorded");
  });

  it("should track total records and batches", async function () {
    const hashes = [
      ethers.keccak256(ethers.toUtf8Bytes("data1")),
      ethers.keccak256(ethers.toUtf8Bytes("data2")),
    ];

    await registry.connect(ledgerAgent).recordHash(hashes[0], "election", "test1");
    await registry.connect(ledgerAgent).recordHash(hashes[1], "budget", "test2");
    await registry.connect(ledgerAgent).recordBatch("batch-001", [hashes[0], hashes[1]], "procurement");

    const stats = await registry.getStats();
    expect(stats.totalBatches).to.equal(1);
  });

  it("should transfer ownership", async function () {
    await registry.transferOwnership(ledgerAgent.address);
    expect(await registry.owner()).to.equal(ledgerAgent.address);
  });
});
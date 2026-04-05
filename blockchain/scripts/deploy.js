const hre = require("hardhat");

async function main() {
  console.log("Deploying TransparencyRegistry to", hre.network.name);

  const TransparencyRegistry = await hre.ethers.getContractFactory("TransparencyRegistry");
  const registry = await TransparencyRegistry.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log("TransparencyRegistry deployed to:", address);

  // Verify on Etherscan (for testnet/mainnet)
  if (hre.network.name !== "hardhat") {
    console.log("Waiting for block confirmations...");
    await registry.deploymentTransaction().wait(5);

    console.log("Verifying contract on Etherscan...");
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [],
    });
  }

  console.log("\n⚠️  IMPORTANT: Save this contract address!");
  console.log("Update your .env with: CONTRACT_ADDRESS=", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

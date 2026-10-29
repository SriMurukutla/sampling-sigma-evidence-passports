import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { network } from "hardhat";

const UNIT = 10n ** 18n;

describe("SamplingSigma", async function () {
  const { viem } = await network.create();
  const [admin, treasury, user] = await viem.getWalletClients();

  async function deploy() {
    return viem.deployContract("SamplingSigma", [
      admin.account.address,
      treasury.account.address,
      1_000_000n * UNIT,
    ]);
  }

  it("creates the declared fixed initial allocation under the cap", async function () {
    const token = await deploy();
    assert.equal(await token.read.name(), "Sampling Sigma");
    assert.equal(await token.read.symbol(), "SIGMA");
    assert.equal(await token.read.totalSupply(), 1_000_000n * UNIT);
    assert.equal(await token.read.balanceOf([treasury.account.address]), 1_000_000n * UNIT);
  });

  it("has no post-deployment mint function", async function () {
    const artifact = await viem.getContractAt("SamplingSigma", (await deploy()).address);
    assert.equal("mint" in artifact.write, false);
  });

  it("rejects a shared administrator and treasury", async function () {
    await assert.rejects(
      viem.deployContract("SamplingSigma", [
        admin.account.address,
        admin.account.address,
        1_000_000n * UNIT,
      ]),
    );
  });

  it("rejects unauthorized pause operations", async function () {
    const token = await deploy();
    await assert.rejects(token.write.pause({ account: user.account }));
  });

  it("blocks transfers while paused and restores them after unpause", async function () {
    const token = await deploy();
    await token.write.pause({ account: admin.account });
    await assert.rejects(
      token.write.transfer([user.account.address, UNIT], { account: treasury.account }),
    );
    await token.write.unpause({ account: admin.account });
    await token.write.transfer([user.account.address, UNIT], { account: treasury.account });
    assert.equal(await token.read.balanceOf([user.account.address]), UNIT);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { network } from "hardhat";
import { keccak256, stringToHex } from "viem";

const h = (value: string) => keccak256(stringToHex(value));

describe("SamplingSigmaAssuranceCore", async function () {
  const { viem } = await network.create();
  const [admin, issuer, reviewer] = await viem.getWalletClients();
  async function deploy() {
    const core = await viem.deployContract("SamplingSigmaAssuranceCore", [admin.account.address]);
    await core.write.grantRole([await core.read.ISSUER_ROLE(), issuer.account.address], { account: admin.account });
    await core.write.grantRole([await core.read.REVIEWER_ROLE(), reviewer.account.address], { account: admin.account });
    return core;
  }
  async function submit(core: Awaited<ReturnType<typeof deploy>>, artifact = "artifact-v1") {
    const now = BigInt(Math.floor(Date.now() / 1000));
    await core.write.submitPassport([h("SUPPLY_CHAIN"), h(artifact), h("scope"), h("limitations"), h("subject-1"), now + 86400n], { account: issuer.account });
  }

  it("records complete assurance commitments and independent review", async function () {
    const core = await deploy(); await submit(core);
    await core.write.reviewPassport([1n, 1, h("review"), h("reviewer-org"), h("conflict-none")], { account: reviewer.account });
    const [passport, evidence] = await core.read.getPassport([1n]);
    assert.equal(passport.status, 1); assert.equal(passport.reviewer.toLowerCase(), reviewer.account.address.toLowerCase());
    assert.equal(evidence.reviewerOrganizationHash, h("reviewer-org"));
    assert.equal(await core.read.isCurrent([1n]), true);
  });

  it("prevents issuer self-review", async function () {
    const core = await deploy(); await submit(core);
    await assert.rejects(core.write.reviewPassport([1n, 1, h("review"), h("org"), h("conflict")], { account: issuer.account }));
  });

  it("requires scope limitations identity and review evidence commitments", async function () {
    const core = await deploy(); const now = BigInt(Math.floor(Date.now() / 1000));
    await assert.rejects(core.write.submitPassport([h("DOMAIN"), h("artifact"), h("scope"), h("limitations"), h("subject"), now - 1n], { account: issuer.account }));
    await submit(core);
    await assert.rejects(core.write.reviewPassport([1n, 1, h("review"), h("org"), `0x${"00".repeat(32)}`], { account: reviewer.account }));
  });

  it("preserves explicit supersession lineage", async function () {
    const core = await deploy(); await submit(core, "artifact-v1"); await submit(core, "artifact-v2");
    for (const id of [1n, 2n]) await core.write.reviewPassport([id, 1, h(`review-${id}`), h("org"), h("conflict")], { account: reviewer.account });
    await core.write.supersedePassport([1n, 2n], { account: reviewer.account });
    const [oldPassport] = await core.read.getPassport([1n]);
    assert.equal(oldPassport.status, 4); assert.equal(oldPassport.supersededBy, 2n);
  });
});

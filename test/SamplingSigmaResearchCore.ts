import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { network } from "hardhat";
import { keccak256, stringToHex } from "viem";

const digest = (value: string) => keccak256(stringToHex(value));

describe("SamplingSigmaResearchCore", async function () {
  const { viem } = await network.create();
  const [admin, researcher, validator, outsider] = await viem.getWalletClients();

  async function deploy() {
    return viem.deployContract("SamplingSigmaResearchCore", [admin.account.address]);
  }

  it("records and validates cybersecurity research evidence", async function () {
    const core = await deploy();
    const researcherRole = await core.read.RESEARCHER_ROLE();
    const validatorRole = await core.read.VALIDATOR_ROLE();
    const domain = await core.read.THREAT_RESEARCH();
    await core.write.grantRole([researcherRole, researcher.account.address], {
      account: admin.account,
    });
    await core.write.grantRole([validatorRole, validator.account.address], {
      account: admin.account,
    });

    await core.write.submitResearch([domain, digest("artifact-v1")], {
      account: researcher.account,
    });
    await core.write.reviewResearch([1n, 1, digest("validation-evidence-v1")], {
      account: validator.account,
    });

    const record = await core.read.getResearch([1n]);
    assert.equal(record.submitter.toLowerCase(), researcher.account.address.toLowerCase());
    assert.equal(record.domain, domain);
    assert.equal(record.state, 1);
    assert.notEqual(record.reviewedAt, 0n);
  });

  it("rejects submissions from accounts without the research role", async function () {
    const core = await deploy();
    const domain = await core.read.CRYPTOGRAPHY();
    await assert.rejects(
      core.write.submitResearch([domain, digest("unauthorized")], {
        account: outsider.account,
      }),
    );
  });

  it("does not allow a reviewed record to be silently rewritten", async function () {
    const core = await deploy();
    const domain = await core.read.AI_SECURITY();
    const researcherRole = await core.read.RESEARCHER_ROLE();
    await core.write.grantRole([researcherRole, researcher.account.address], { account: admin.account });
    await core.write.submitResearch([domain, digest("model-security-study")], {
      account: researcher.account,
    });
    await core.write.reviewResearch([1n, 2, digest("rejection-evidence")], {
      account: admin.account,
    });
    await assert.rejects(
      core.write.reviewResearch([1n, 1, digest("replacement-evidence")], {
        account: admin.account,
      }),
    );
  });

  it("permits explicit supersession of previously validated research", async function () {
    const core = await deploy();
    const domain = await core.read.SOFTWARE_SUPPLY_CHAIN();
    const researcherRole = await core.read.RESEARCHER_ROLE();
    await core.write.grantRole([researcherRole, researcher.account.address], { account: admin.account });
    await core.write.submitResearch([domain, digest("sbom-method-v1")], {
      account: researcher.account,
    });
    await core.write.reviewResearch([1n, 1, digest("review-v1")], {
      account: admin.account,
    });
    await core.write.supersedeResearch([1n, digest("supersession-rationale-v2")], {
      account: admin.account,
    });

    const record = await core.read.getResearch([1n]);
    assert.equal(record.state, 3);
  });

  it("prevents a researcher from validating their own submission", async function () {
    const core = await deploy();
    const domain = await core.read.IDENTITY_SECURITY();
    await core.write.submitResearch([domain, digest("identity-study")], { account: admin.account });
    await assert.rejects(
      core.write.reviewResearch([1n, 1, digest("self-review")], { account: admin.account }),
    );
  });

  it("rejects unregistered research domains", async function () {
    const core = await deploy();
    await assert.rejects(
      core.write.submitResearch([digest("UNREGISTERED_DOMAIN"), digest("artifact")], {
        account: admin.account,
      }),
    );
  });
});

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {AccessControlDefaultAdminRules} from "@openzeppelin/contracts/access/extensions/AccessControlDefaultAdminRules.sol";

/// @title Sampling Sigma Assurance Core
/// @notice Records privacy-preserving commitments for independently reviewed cybersecurity evidence.
/// @dev A valid record proves integrity and review lineage, not the truth or sufficiency of the underlying assessment.
contract SamplingSigmaAssuranceCore is AccessControlDefaultAdminRules {
    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");
    bytes32 public constant REVIEWER_ROLE = keccak256("REVIEWER_ROLE");

    enum Status { Submitted, Validated, Rejected, Revoked, Superseded }

    struct Passport {
        bytes32 artifactHash;
        bytes32 scopeHash;
        bytes32 limitationsHash;
        bytes32 domain;
        bytes32 subjectIdHash;
        address issuer;
        address reviewer;
        uint64 issuedAt;
        uint64 validUntil;
        uint64 reviewedAt;
        uint256 supersededBy;
        Status status;
    }

    struct ReviewEvidence {
        bytes32 evidenceHash;
        bytes32 reviewerOrganizationHash;
        bytes32 conflictDisclosureHash;
    }

    error EmptyCommitment();
    error InvalidValidityPeriod();
    error UnknownPassport(uint256 passportId);
    error InvalidTransition();
    error SelfReviewNotAllowed();
    error SupersessionMismatch();

    uint256 public nextPassportId = 1;
    mapping(uint256 => Passport) private _passports;
    mapping(uint256 => ReviewEvidence) private _reviewEvidence;

    event PassportSubmitted(uint256 indexed passportId, bytes32 indexed domain, bytes32 indexed artifactHash, address issuer, uint64 validUntil);
    event PassportReviewed(uint256 indexed passportId, Status status, bytes32 evidenceHash, address reviewer);
    event PassportRevoked(uint256 indexed passportId, bytes32 indexed reasonHash, address reviewer);
    event PassportSuperseded(uint256 indexed passportId, uint256 indexed replacementPassportId, address reviewer);

    constructor(address admin) AccessControlDefaultAdminRules(2 days, admin) {
        if (admin == address(0)) revert AccessControlInvalidDefaultAdmin(address(0));
        _grantRole(ISSUER_ROLE, admin);
        _grantRole(REVIEWER_ROLE, admin);
    }

    function submitPassport(
        bytes32 domain,
        bytes32 artifactHash,
        bytes32 scopeHash,
        bytes32 limitationsHash,
        bytes32 subjectIdHash,
        uint64 validUntil
    ) external onlyRole(ISSUER_ROLE) returns (uint256 passportId) {
        if (domain == bytes32(0) || artifactHash == bytes32(0) || scopeHash == bytes32(0) || limitationsHash == bytes32(0) || subjectIdHash == bytes32(0)) revert EmptyCommitment();
        if (validUntil <= block.timestamp) revert InvalidValidityPeriod();
        passportId = nextPassportId++;
        _passports[passportId] = Passport({
            artifactHash: artifactHash,
            scopeHash: scopeHash,
            limitationsHash: limitationsHash,
            domain: domain,
            subjectIdHash: subjectIdHash,
            issuer: msg.sender,
            reviewer: address(0),
            issuedAt: uint64(block.timestamp),
            validUntil: validUntil,
            reviewedAt: 0,
            supersededBy: 0,
            status: Status.Submitted
        });
        emit PassportSubmitted(passportId, domain, artifactHash, msg.sender, validUntil);
    }

    function reviewPassport(
        uint256 passportId,
        Status decision,
        bytes32 evidenceHash,
        bytes32 reviewerOrganizationHash,
        bytes32 conflictDisclosureHash
    ) external onlyRole(REVIEWER_ROLE) {
        Passport storage passport = _passport(passportId);
        if (passport.status != Status.Submitted || (decision != Status.Validated && decision != Status.Rejected)) revert InvalidTransition();
        if (passport.issuer == msg.sender) revert SelfReviewNotAllowed();
        if (evidenceHash == bytes32(0) || reviewerOrganizationHash == bytes32(0) || conflictDisclosureHash == bytes32(0)) revert EmptyCommitment();
        passport.status = decision;
        passport.reviewer = msg.sender;
        passport.reviewedAt = uint64(block.timestamp);
        _reviewEvidence[passportId] = ReviewEvidence(evidenceHash, reviewerOrganizationHash, conflictDisclosureHash);
        emit PassportReviewed(passportId, decision, evidenceHash, msg.sender);
    }

    function revokePassport(uint256 passportId, bytes32 reasonHash) external onlyRole(REVIEWER_ROLE) {
        Passport storage passport = _passport(passportId);
        if (passport.status != Status.Validated || reasonHash == bytes32(0)) revert InvalidTransition();
        passport.status = Status.Revoked;
        emit PassportRevoked(passportId, reasonHash, msg.sender);
    }

    function supersedePassport(uint256 passportId, uint256 replacementPassportId) external onlyRole(REVIEWER_ROLE) {
        Passport storage passport = _passport(passportId);
        Passport storage replacement = _passport(replacementPassportId);
        if (passport.status != Status.Validated || replacement.status != Status.Validated) revert InvalidTransition();
        if (passportId == replacementPassportId || passport.subjectIdHash != replacement.subjectIdHash || replacement.issuedAt < passport.issuedAt) revert SupersessionMismatch();
        passport.status = Status.Superseded;
        passport.supersededBy = replacementPassportId;
        emit PassportSuperseded(passportId, replacementPassportId, msg.sender);
    }

    function getPassport(uint256 passportId) external view returns (Passport memory, ReviewEvidence memory) {
        return (_passport(passportId), _reviewEvidence[passportId]);
    }

    function isCurrent(uint256 passportId) external view returns (bool) {
        Passport storage passport = _passport(passportId);
        return passport.status == Status.Validated && passport.validUntil >= block.timestamp;
    }

    function _passport(uint256 passportId) private view returns (Passport storage passport) {
        passport = _passports[passportId];
        if (passport.issuer == address(0)) revert UnknownPassport(passportId);
    }
}

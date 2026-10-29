// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {AccessControlDefaultAdminRules} from "@openzeppelin/contracts/access/extensions/AccessControlDefaultAdminRules.sol";

/// @title Sampling Sigma Research Core
/// @notice Evidence registry for governed cybersecurity research and validation.
/// @dev Stores hashes and review state, not confidential research content.
contract SamplingSigmaResearchCore is AccessControlDefaultAdminRules {
    bytes32 public constant RESEARCHER_ROLE = keccak256("RESEARCHER_ROLE");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");

    bytes32 public constant THREAT_RESEARCH = keccak256("THREAT_RESEARCH");
    bytes32 public constant CRYPTOGRAPHY = keccak256("CRYPTOGRAPHY");
    bytes32 public constant IDENTITY_SECURITY = keccak256("IDENTITY_SECURITY");
    bytes32 public constant SOFTWARE_SUPPLY_CHAIN = keccak256("SOFTWARE_SUPPLY_CHAIN");
    bytes32 public constant INCIDENT_RESPONSE = keccak256("INCIDENT_RESPONSE");
    bytes32 public constant AI_SECURITY = keccak256("AI_SECURITY");

    enum ReviewState {
        Submitted,
        Validated,
        Rejected,
        Superseded
    }

    struct ResearchRecord {
        bytes32 artifactHash;
        bytes32 evidenceHash;
        bytes32 domain;
        address submitter;
        uint64 submittedAt;
        uint64 reviewedAt;
        ReviewState state;
    }

    error EmptyHash();
    error UnknownRecord(uint256 recordId);
    error RecordAlreadyReviewed(uint256 recordId);
    error InvalidReviewState();
    error UnsupportedDomain(bytes32 domain);
    error SelfReviewNotAllowed(uint256 recordId);

    uint256 public nextRecordId = 1;
    mapping(uint256 recordId => ResearchRecord record) private _records;

    event ResearchSubmitted(
        uint256 indexed recordId,
        bytes32 indexed domain,
        bytes32 indexed artifactHash,
        address submitter
    );
    event ResearchReviewed(
        uint256 indexed recordId,
        ReviewState state,
        bytes32 evidenceHash,
        address validator
    );

    constructor(address admin) AccessControlDefaultAdminRules(2 days, admin) {
        if (admin == address(0)) revert AccessControlInvalidDefaultAdmin(address(0));
        _grantRole(RESEARCHER_ROLE, admin);
        _grantRole(VALIDATOR_ROLE, admin);
    }

    function submitResearch(bytes32 domain, bytes32 artifactHash)
        external
        onlyRole(RESEARCHER_ROLE)
        returns (uint256 recordId)
    {
        if (domain == bytes32(0) || artifactHash == bytes32(0)) revert EmptyHash();
        if (!_supportedDomain(domain)) revert UnsupportedDomain(domain);

        recordId = nextRecordId++;
        _records[recordId] = ResearchRecord({
            artifactHash: artifactHash,
            evidenceHash: bytes32(0),
            domain: domain,
            submitter: msg.sender,
            submittedAt: uint64(block.timestamp),
            reviewedAt: 0,
            state: ReviewState.Submitted
        });

        emit ResearchSubmitted(recordId, domain, artifactHash, msg.sender);
    }

    function reviewResearch(uint256 recordId, ReviewState state, bytes32 evidenceHash)
        external
        onlyRole(VALIDATOR_ROLE)
    {
        ResearchRecord storage record = _record(recordId);
        if (record.submitter == msg.sender) revert SelfReviewNotAllowed(recordId);
        if (record.state != ReviewState.Submitted) revert RecordAlreadyReviewed(recordId);
        if (state != ReviewState.Validated && state != ReviewState.Rejected) {
            revert InvalidReviewState();
        }
        if (evidenceHash == bytes32(0)) revert EmptyHash();

        record.state = state;
        record.evidenceHash = evidenceHash;
        record.reviewedAt = uint64(block.timestamp);

        emit ResearchReviewed(recordId, state, evidenceHash, msg.sender);
    }

    function supersedeResearch(uint256 recordId, bytes32 evidenceHash)
        external
        onlyRole(VALIDATOR_ROLE)
    {
        ResearchRecord storage record = _record(recordId);
        if (record.state != ReviewState.Validated) revert InvalidReviewState();
        if (evidenceHash == bytes32(0)) revert EmptyHash();

        record.state = ReviewState.Superseded;
        record.evidenceHash = evidenceHash;
        record.reviewedAt = uint64(block.timestamp);

        emit ResearchReviewed(recordId, ReviewState.Superseded, evidenceHash, msg.sender);
    }

    function getResearch(uint256 recordId) external view returns (ResearchRecord memory) {
        return _record(recordId);
    }

    function isSupportedDomain(bytes32 domain) external pure returns (bool) {
        return _supportedDomain(domain);
    }

    function _supportedDomain(bytes32 domain) private pure returns (bool) {
        return domain == THREAT_RESEARCH || domain == CRYPTOGRAPHY
            || domain == IDENTITY_SECURITY || domain == SOFTWARE_SUPPLY_CHAIN
            || domain == INCIDENT_RESPONSE || domain == AI_SECURITY;
    }

    function _record(uint256 recordId) private view returns (ResearchRecord storage record) {
        record = _records[recordId];
        if (record.submitter == address(0)) revert UnknownRecord(recordId);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {AccessControlDefaultAdminRules} from "@openzeppelin/contracts/access/extensions/AccessControlDefaultAdminRules.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Pausable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/// @title Sampling Sigma
/// @notice Capped protocol asset for the Sampling Sigma cybersecurity network.
/// @dev Non-upgradeable by design. Administrative authority should be moved to
///      an independently controlled multisignature before production use.
contract SamplingSigma is
    ERC20,
    ERC20Burnable,
    ERC20Pausable,
    ERC20Permit,
    AccessControlDefaultAdminRules
{
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    error ZeroAddress();
    error ZeroSupply();
    error SharedAdminAndTreasury();

    constructor(
        address admin,
        address treasury,
        uint256 fixedSupply
    )
        ERC20("Sampling Sigma", "SIGMA")
        ERC20Permit("Sampling Sigma")
        AccessControlDefaultAdminRules(2 days, admin)
    {
        if (admin == address(0) || treasury == address(0)) revert ZeroAddress();
        if (admin == treasury) revert SharedAdminAndTreasury();
        if (fixedSupply == 0) revert ZeroSupply();

        _grantRole(PAUSER_ROLE, admin);
        _mint(treasury, fixedSupply);
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Pausable)
    {
        super._update(from, to, value);
    }
}

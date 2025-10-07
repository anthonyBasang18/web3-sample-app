// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

// Import OpenZeppelin contracts
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Your contract inherits from ERC20 and Ownable
contract MyToken is ERC20, Ownable {
    // Maximum supply: 1 million tokens
    uint256 public constant MAX_SUPPLY = 1000000 * 10**18;
    
    // Constructor - runs once when deployed
    constructor() ERC20("My Token", "MTK") Ownable(msg.sender) {
        // Mint 100,000 tokens to yourself
        _mint(msg.sender, 100000 * 10**18);
    }
    
    // Owner can mint tokens
    function mint(address to, uint256 amount) public onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }
    
    // Anyone can mint (limited to 1000 tokens)
    function publicMint(uint256 amount) public {
        require(amount <= 1000 * 10**18, "Max 1000 tokens per mint");
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(msg.sender, amount);
    }
}

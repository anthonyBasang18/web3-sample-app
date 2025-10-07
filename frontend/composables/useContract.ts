import { ethers } from 'ethers'

/**
 * Contract Composable
 * Handles smart contract interactions using ethers.js
 */

// ERC-20 Token ABI (Human-Readable ABI format)
const TOKEN_ABI = [
  // Read-only functions
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  
  // Write functions
  "function publicMint(uint256 amount)",
  "function transfer(address to, uint256 amount) returns (bool)",
  
  // Events
  "event Transfer(address indexed from, address indexed to, uint256 value)"
]

export const useContract = () => {
  const config = useRuntimeConfig()
  const { getSigner, getProvider } = useWallet()
  
  const contractAddress = config.public.contractAddress
  
  /**
   * Get contract instance with signer (for write operations)
   */
  const getContract = () => {
    const signer = getSigner()
    if (!signer || !contractAddress) {
      throw new Error('Wallet not connected or contract address not set')
    }
    
    return new ethers.Contract(contractAddress, TOKEN_ABI, signer)
  }

  /**
   * Get contract instance with provider (for read-only operations)
   */
  const getReadOnlyContract = () => {
    const provider = getProvider()
    if (!provider) {
      throw new Error('Provider not available')
    }
    
    if (!contractAddress) {
      throw new Error('Contract address not set')
    }
    
    return new ethers.Contract(contractAddress, TOKEN_ABI, provider)
  }

  /**
   * Mint tokens (max 1000 per transaction)
   * @param amount - Amount of tokens to mint
   * @returns Transaction hash
   */
  const mintTokens = async (amount: string | number) => {
    try {
      const contract = getContract()
      
      // Convert amount to Wei (18 decimals)
      const amountWei = ethers.utils.parseEther(String(amount))
      
      // Send transaction
      const tx = await contract.publicMint(amountWei)
      
      // Wait for confirmation
      await tx.wait()
      
      return tx.hash
    } catch (error) {
      console.error('Mint failed:', error)
      throw error
    }
  }

  /**
   * Transfer tokens to another address
   * @param to - Recipient address
   * @param amount - Amount of tokens to transfer
   * @returns Transaction hash
   */
  const transferTokens = async (to: string, amount: string | number) => {
    try {
      const contract = getContract()
      
      // Convert amount to Wei
      const amountWei = ethers.utils.parseEther(String(amount))
      
      // Send transaction
      const tx = await contract.transfer(to, amountWei)
      
      // Wait for confirmation
      await tx.wait()
      
      return tx.hash
    } catch (error) {
      console.error('Transfer failed:', error)
      throw error
    }
  }

  /**
   * Get token balance for an address
   * @param address - Wallet address
   * @returns Token balance in human-readable format
   */
  const getTokenBalance = async (address: string) => {
    try {
      const contract = getReadOnlyContract()
      const balance = await contract.balanceOf(address)
      
      // Convert from Wei to human-readable format
      return ethers.utils.formatEther(balance)
    } catch (error) {
      console.error('Failed to get token balance:', error)
      throw error
    }
  }

  /**
   * Get token metadata (name, symbol, supply)
   * @returns Token information object
   */
  const getTokenInfo = async () => {
    try {
      const contract = getReadOnlyContract()
      
      // Fetch all token info in parallel
      const [name, symbol, decimals, totalSupply] = await Promise.all([
        contract.name(),
        contract.symbol(),
        contract.decimals(),
        contract.totalSupply()
      ])
      
      return {
        name,
        symbol,
        decimals,
        totalSupply: ethers.utils.formatEther(totalSupply)
      }
    } catch (error) {
      console.error('Failed to get token info:', error)
      throw error
    }
  }

  return {
    contractAddress,
    mintTokens,
    transferTokens,
    getTokenBalance,
    getTokenInfo
  }
}
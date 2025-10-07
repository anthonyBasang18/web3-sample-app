import { ethers } from 'ethers'

/**
 * Wallet Composable
 * Handles MetaMask connection and wallet state
 */

// Store provider and signer outside Vue reactivity to avoid proxy issues
let walletProvider: any = null
let walletSigner: any = null

export const useWallet = () => {
  // Reactive state
  const isConnected = ref(false)
  const account = ref('')
  const balance = ref('0')
  const network = ref('')

  /**
   * Switch to Sepolia testnet
   */
  const switchToSepolia = async () => {
    const SEPOLIA_CHAIN_ID = '0xaa36a7'
    
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: SEPOLIA_CHAIN_ID }],
      })
    } catch (error: any) {
      // If chain not added, add it
      if (error.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: SEPOLIA_CHAIN_ID,
            chainName: 'Sepolia',
            nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
            rpcUrls: ['https://sepolia.infura.io/v3/'],
            blockExplorerUrls: ['https://sepolia.etherscan.io']
          }]
        })
      } else {
        throw error
      }
    }
  }

  /**
   * Connect to MetaMask wallet
   */
  const connectWallet = async () => {
    if (!window.ethereum) {
      throw new Error('MetaMask not found. Please install MetaMask extension.')
    }

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })

      if (accounts.length > 0) {
        account.value = accounts[0]
        
        // Initialize ethers provider and signer
        walletProvider = new ethers.providers.Web3Provider(window.ethereum)
        walletSigner = walletProvider.getSigner()
        isConnected.value = true
        
        await updateBalance()
      }
    } catch (error) {
      console.error('Failed to connect wallet:', error)
      throw error
    }
  }

  /**
   * Update ETH balance and network info
   */
  const updateBalance = async () => {
    if (!account.value) return
    
    try {
      // Create fresh provider to avoid Vue reactivity issues
      const tempProvider = new ethers.providers.Web3Provider(window.ethereum)
      
      // Get balance in ETH
      const balanceWei = await tempProvider.getBalance(account.value)
      balance.value = ethers.utils.formatEther(balanceWei)
      
      // Get network name
      const net = await tempProvider.getNetwork()
      network.value = net.name === 'unknown' ? `Chain ID: ${net.chainId}` : net.name
    } catch (error) {
      console.error('Failed to update balance:', error)
    }
  }

  /**
   * Disconnect wallet and clear state
   */
  const disconnect = () => {
    isConnected.value = false
    account.value = ''
    balance.value = '0'
    network.value = ''
    walletProvider = null
    walletSigner = null
  }

  /**
   * Check if wallet is already connected on page load
   */
  onMounted(async () => {
    if (typeof window !== 'undefined' && window.ethereum) {
      try {
        // Check for existing connection
        const accounts = await window.ethereum.request({
          method: 'eth_accounts'
        })
        
        if (accounts.length > 0) {
          account.value = accounts[0]
          walletProvider = new ethers.providers.Web3Provider(window.ethereum)
          walletSigner = walletProvider.getSigner()
          isConnected.value = true
          await updateBalance()
        }
      } catch (error) {
        console.error('Failed to check existing connection:', error)
      }
    }
  })

  /**
   * Get provider and signer (not reactive)
   */
  const getProvider = () => walletProvider
  const getSigner = () => walletSigner

  // Return readonly state and methods
  return {
    // State (readonly to prevent external modification)
    isConnected: readonly(isConnected),
    account: readonly(account),
    balance: readonly(balance),
    network: readonly(network),
    
    // Methods
    getProvider,
    getSigner,
    connectWallet,
    switchToSepolia,
    updateBalance,
    disconnect
  }
}
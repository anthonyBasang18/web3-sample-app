/**
 * API Composable
 * Handles backend API calls
 */

export const useApi = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  /**
   * Get blockchain metadata (gas price, block number)
   * @returns Chain metadata from backend
   */
  const getChainMeta = async () => {
    try {
      const data = await $fetch(`${apiUrl}/chain/meta`)
      return data
    } catch (error) {
      console.error('Failed to fetch chain metadata:', error)
      throw error
    }
  }

  /**
   * Get ETH balance for an address
   * @param address - Wallet address
   * @returns Balance information
   */
  const getAccountBalance = async (address: string) => {
    try {
      const data = await $fetch(`${apiUrl}/account/${address}`)
      return data
    } catch (error) {
      console.error('Failed to fetch account balance:', error)
      throw error
    }
  }

  /**
   * Get transaction history for an address
   * @param address - Wallet address
   * @returns List of transactions
   */
  const getAccountTransactions = async (address: string) => {
    try {
      const data = await $fetch(`${apiUrl}/account/${address}/txs`)
      return data
    } catch (error) {
      console.error('Failed to fetch transactions:', error)
      throw error
    }
  }

  return {
    getChainMeta,
    getAccountBalance,
    getAccountTransactions
  }
}
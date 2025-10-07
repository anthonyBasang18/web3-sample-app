declare global {
  interface Window {
    ethereum?: any
  }
}

export const formatAddress = (address: string): string => {
  if (!address) return ''
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

export const formatBalance = (balance: string, decimals: number = 4): string => {
  const num = parseFloat(balance)
  return num.toFixed(decimals)
}

export const isValidAddress = (address: string): boolean => {
  return /^0x[a-fA-F0-9]{40}$/.test(address)
}
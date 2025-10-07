<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-black text-white py-6">
      <div class="max-w-lg mx-auto px-4">
        <h1 class="text-2xl font-semibold text-center mb-2">Ardata Tech Exam</h1>
        <p class="text-center text-sm text-gray-400">Sepolia Testnet</p>
      </div>
    </header>

    <main class="max-w-lg mx-auto px-4 py-8 space-y-4">
      <!-- Instructions -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
        <h3 class="font-semibold mb-2">📋 Instructions:</h3>
        <ol class="list-decimal list-inside space-y-1 text-gray-700">
          <li>Connect your MetaMask wallet</li>
          <li>Make sure you're on Sepolia testnet</li>
          <li>Get free Sepolia ETH from <a href="https://sepoliafaucet.com" target="_blank" class="text-blue-600 underline">faucet</a></li>
          <li>Mint tokens (max 1000 per transaction)</li>
          <li>Transfer tokens to other addresses</li>
        </ol>
      </div>

      <!-- Network Warning -->
      <div v-if="isConnected && network !== 'sepolia'" class="bg-yellow-50 border border-yellow-300 rounded-lg p-4">
        <p class="text-sm text-yellow-800 mb-2">⚠️ Wrong network detected: {{ network }}</p>
        <p class="text-sm text-yellow-700 mb-3">Please switch to Sepolia testnet</p>
        <button @click="switchToSepolia" class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm">
          Switch to Sepolia
        </button>
      </div>

      <!-- Connect Wallet -->
      <div v-if="!isConnected" class="bg-white border border-gray-200 rounded-lg p-6">
        <button @click="handleConnect" :disabled="connecting" 
          class="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 disabled:bg-gray-300">
          {{ connecting ? 'Connecting...' : 'Connect Wallet' }}
        </button>
      </div>

      <!-- Wallet Info -->
      <div v-if="isConnected" class="bg-white border border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold">Wallet</h2>
          <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">{{ network || 'Connected' }}</span>
        </div>
        <div class="space-y-3">
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600 text-sm">Address</span>
            <code class="text-sm">{{ account.slice(0, 6) }}...{{ account.slice(-4) }}</code>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600 text-sm">ETH Balance</span>
            <span class="font-medium">{{ parseFloat(balance).toFixed(4) }} ETH</span>
          </div>
          <div v-if="tokenInfo" class="flex justify-between py-2">
            <span class="text-gray-600 text-sm">{{ tokenInfo.symbol }} Balance</span>
            <span class="font-medium">{{ parseFloat(tokenBalance).toFixed(2) }} {{ tokenInfo.symbol }}</span>
          </div>
        </div>
        <button @click="disconnect" 
          class="w-full mt-4 border border-black text-black py-2 rounded-lg hover:bg-gray-50">
          Disconnect
        </button>
      </div>

      <!-- Mint Tokens -->
      <div v-if="isConnected" class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-lg font-semibold mb-4">Mint Tokens</h2>
        <input v-model="mintAmount" type="number" placeholder="Amount (max 1000)" max="1000"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 mb-3 focus:outline-none focus:border-black" />
        <button @click="handleMint" :disabled="minting || !mintAmount"
          class="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 disabled:bg-gray-300">
          {{ minting ? 'Minting...' : 'Mint' }}
        </button>
      </div>

      <!-- Transfer Tokens -->
      <div v-if="isConnected" class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-lg font-semibold mb-4">Transfer Tokens</h2>
        <input v-model="transferTo" type="text" placeholder="Recipient address (0x...)"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 mb-3 focus:outline-none focus:border-black" />
        <input v-model="transferAmount" type="number" placeholder="Amount" step="0.01"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 mb-3 focus:outline-none focus:border-black" />
        <button @click="handleTransfer" :disabled="transferring || !transferTo || !transferAmount"
          class="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 disabled:bg-gray-300">
          {{ transferring ? 'Transferring...' : 'Transfer' }}
        </button>
      </div>

      <!-- Transaction History -->
      <div v-if="isConnected" class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-lg font-semibold mb-4">Recent Transactions</h2>
        <div v-if="transactions.length > 0" class="space-y-2">
          <div v-for="tx in transactions" :key="tx.hash" class="border-b pb-2 last:border-b-0">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Hash</span>
              <code class="text-xs">{{ tx.hash?.slice(0, 10) }}...</code>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Value</span>
              <span>{{ tx.value }} {{ tx.asset }}</span>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500 text-center py-4">
          No transactions found. Try minting or transferring tokens!
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4">
        {{ error }}
      </div>
    </main>
  </div>
</template>

<script setup>
const { isConnected, account, balance, network, connectWallet, switchToSepolia, disconnect, updateBalance } = useWallet()
const { mintTokens, transferTokens, getTokenBalance, getTokenInfo } = useContract()
const { getAccountTransactions } = useApi()

const connecting = ref(false)
const minting = ref(false)
const transferring = ref(false)
const error = ref('')

const mintAmount = ref('')
const transferTo = ref('')
const transferAmount = ref('')

const tokenInfo = ref(null)
const tokenBalance = ref('0')
const transactions = ref([])

const handleConnect = async () => {
  connecting.value = true
  error.value = ''
  
  try {
    await connectWallet()
    await loadTokenData()
    await loadTransactions()
  } catch (err) {
    error.value = err.message || 'Failed to connect wallet'
  } finally {
    connecting.value = false
  }
}

const handleMint = async () => {
  minting.value = true
  error.value = ''
  
  try {
    const txHash = await mintTokens(mintAmount.value)
    console.log('Mint transaction:', txHash)
    
    // Refresh balances and transactions
    await updateBalance()
    await loadTokenData()
    await loadTransactions()
    
    mintAmount.value = ''
  } catch (err) {
    error.value = err.message || 'Failed to mint tokens'
  } finally {
    minting.value = false
  }
}

const handleTransfer = async () => {
  transferring.value = true
  error.value = ''
  
  try {
    const txHash = await transferTokens(transferTo.value, transferAmount.value)
    console.log('Transfer transaction:', txHash)
    
    // Refresh balances and transactions
    await updateBalance()
    await loadTokenData()
    await loadTransactions()
    
    transferTo.value = ''
    transferAmount.value = ''
  } catch (err) {
    error.value = err.message || 'Failed to transfer tokens'
  } finally {
    transferring.value = false
  }
}

const loadTokenData = async () => {
  if (!account.value) return
  
  // Skip token data if no contract deployed
  const config = useRuntimeConfig()
  if (!config.public.contractAddress) {
    return
  }
  
  try {
    const [info, balance] = await Promise.all([
      getTokenInfo(),
      getTokenBalance(account.value)
    ])
    
    tokenInfo.value = info
    tokenBalance.value = balance
  } catch (err) {
    // Silently fail if contract not deployed
  }
}

const loadTransactions = async () => {
  if (!account.value) return
  
  try {
    const data = await getAccountTransactions(account.value)
    transactions.value = data.transactions || []
  } catch (err) {
    // Silently fail - new wallets have no transactions
  }
}

watch(account, async (newAccount) => {
  if (newAccount) {
    await loadTokenData()
    await loadTransactions()
  }
})
</script>
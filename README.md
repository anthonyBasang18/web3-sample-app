# Web3 dApp Project

A production-ready full-stack decentralized application demonstrating Web3 integration with ERC-20 token functionality.


## Project Structure

```
web3/
├── frontend/              # Nuxt 3 + TypeScript + Tailwind CSS
│   ├── composables/       # Vue composables (useWallet, useContract, useApi)
│   ├── pages/             # Application pages
│   └── Dockerfile         # Frontend container
├── backend/               # FastAPI + PostgreSQL + Redis
│   ├── models/            # Database models
│   ├── routes/            # API routes (chain, account)
│   ├── services/          # Business logic
│   └── Dockerfile         # Backend container
├── contract/              # Hardhat + Solidity + OpenZeppelin
│   ├── contracts/         # Smart contracts (MyToken.sol)
│   └── ignition/          # Deployment modules
└── docker/                # Docker orchestration
    └── docker-compose.yml # Multi-container setup
```

## Features

- **Frontend**: MetaMask wallet, ETH balance, transaction history, token operations (TypeScript +5)
- **Backend**: RESTful API, chain metadata, account management (Redis +2.5, PostgreSQL +2.5)
- **Smart Contract**: ERC-20 token with minting and transfers (Sepolia testnet +5)
- **Integration**: Full-stack integration with Docker (+5)
- **Architecture**: Modular, documented, production-ready code

## Prerequisites

- **Node.js** 18+ and **Python** 3.9+
- **Docker** & **Docker Compose** (or Colima for macOS)
- **MetaMask** browser extension
- **Alchemy API Key** (https://www.alchemy.com/)
- **Sepolia Test ETH** (https://sepoliafaucet.com/)

## Quick Start

**🔍 Verify Setup First:**
```bash
./verify-setup.sh
```

### 1. Deploy Smart Contract

```bash
cd contract
cp .env.example .env
# Edit .env and add:
# - SEPOLIA_RPC_URL (with your Alchemy API key)
# - SEPOLIA_PRIVATE_KEY (without 0x prefix)

npm install
npx hardhat compile
npx hardhat ignition deploy ignition/modules/MyToken.ts --network sepolia
# Copy the deployed contract address
```

### 2. Setup Environment Variables

```bash
# Docker environment
cp docker/.env.example docker/.env
# Edit docker/.env and add:
# - ALCHEMY_API_KEY (same as contract)
# - CONTRACT_ADDRESS (from step 1)

# Backend environment (for local development)
cp backend/.env.example backend/.env
# Edit backend/.env with same values

# Frontend environment (for local development)  
cp frontend/.env.example frontend/.env
# Edit frontend/.env with CONTRACT_ADDRESS
```

---

## Running the Application

### Option 1: Docker

```bash
cd docker
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Note:** Volume mounts are configured for hot reload. If you encounter mount issues, remove the `volumes:` sections from backend/frontend services in docker-compose.yml

---

### Option 2: Local Development

**Backend:**
```bash
cd backend
cp .env.example .env  # Edit with your values
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
cp .env.example .env  # Edit with your values
npm install
npm run dev
```

**Requires:** PostgreSQL (port 5432) and Redis (port 6379) running locally

---

### Option 3: Hybrid (Docker DB + Local Code)

```bash
# Start only databases
cd docker
docker-compose up postgres redis

# Then run backend/frontend locally (see Option 2)
```

## API Endpoints

- `GET /` - API status
- `GET /chain/meta` - Gas price & block number (Redis cached)
- `GET /account/{address}` - ETH balance (PostgreSQL stored)
- `GET /account/{address}/txs` - Transaction history (last 10)

## Smart Contract Functions

**Read:**
- `name()`, `symbol()`, `decimals()`, `totalSupply()`
- `balanceOf(address)` - Get token balance

**Write:**
- `publicMint(uint256 amount)` - Mint tokens (max 1000)
- `transfer(address to, uint256 amount)` - Transfer tokens

## Architecture

**Tech Stack:**
- Frontend: Nuxt 3, TypeScript, Tailwind CSS, ethers.js v5
- Backend: FastAPI, SQLAlchemy, Web3.py, Redis, PostgreSQL
- Smart Contract: Solidity 0.8.28, OpenZeppelin, Hardhat 3
- DevOps: Docker, Docker Compose

**Data Flow:**
```
User → MetaMask → Smart Contract (Sepolia)
  ↓
Frontend ← → Backend API
              ↓
         PostgreSQL + Redis
```

## Key Architectural Decisions

1. **DB First, Then Sync** - API returns cached data from PostgreSQL immediately, then syncs blockchain in background for better performance
2. **Modular Backend** - Separated concerns into routes, services, and models for maintainability
3. **Composables Pattern** - Vue composables (useWallet, useContract, useApi) for reusable logic
4. **Environment Variables** - All sensitive data externalized to `.env` files
5. **ethers.js v5** - Used v5 instead of v6 for better Nuxt 3 compatibility
6. **Hardhat Ignition** - Used Hardhat 3's deployment system instead of legacy scripts

## Assumptions & Limitations

- Sepolia testnet only (not production mainnet)
- MetaMask browser extension required
- Transaction history: last 50 blocks scanned (recent transactions only)
- Redis cache: 5-minute TTL for chain metadata
- Max token supply: 1,000,000 tokens
- Public mint limit: 1,000 tokens per transaction
- Background sync may take 5-10 seconds to update database

## Known Issues & Solutions

### Development Issues
- **Hot reload**: Remove `/app/.nuxt` volume mount if Nuxt hot reload doesn't work
- **Colima users**: If using external drives, mount them with `colima start --mount /path/to/project:w`
- **Port conflicts**: PostgreSQL uses port 5434 (not default 5432) to avoid conflicts
- **Volume mount issues**: If you encounter binding/mount problems, remove the `volumes:` section from backend and frontend services in docker-compose.yml

### Transaction History Debugging
**Problem**: Frontend showed empty transaction history but API was working

**What I found:**
- Database had 1 transaction, but API queries returned 0 results
- Address case mismatch: DB stored `0x03E425Fa...` but API got `0x03e425fa...`
- Default 50-block scan missed older transactions (address had 13 total txs)
- Sync errors weren't logged, making debugging hard

**Fixes applied:**
```python
# Normalize addresses everywhere
address = w3.to_checksum_address(address)

# Scan more blocks (50 → 1000)
def sync_transactions(address: str, db: Session, block_range: int = 1000):

# Add logging
print(f"Syncing {address} from block {start_block} to {latest_block}")
```

**Key insight**: Ethereum addresses use mixed-case checksums (EIP-55). Always normalize with `w3.to_checksum_address()`.


## References

**Official Documentation:**
- [ethers.js v5](https://docs.ethers.org/v5/) - Ethereum library for frontend
- [Hardhat](https://hardhat.org/docs) - Smart contract development
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Nuxt 3](https://nuxt.com/docs) - Frontend framework
- [OpenZeppelin](https://docs.openzeppelin.com/contracts/) - Smart contract libraries
- [Solidity](https://docs.soliditylang.org/) - Smart contract language

---

# Blockscope API

Backend service for balances and logs


## Features

- Query wallet balance at any block number
- Retrieve smart contract event logs within block ranges
- Multichain support (Avalanche, Ethereum)
- Async implementation
- Redis caching
- Docker


## Prerequisites

- Docker and Docker Compose
- RPC endpoints (Avalanche, Ethereum)

## Installation

### 1. Configure environment variables

Edit `.env` file with your configuration:

```env
# Required: Avalanche RPC endpoint
AVAX_RPC=https://some_rpc

# Optional: Ethereum RPC endpoint (optional, but required for eth support)
ETH_RPC=https://some_rpc

# Smart contract address for event logs
CONTRACT_ADDRESS=0x66357dCaCe80431aee0A7507e2E361B7e2402370
```

### 2. Build and run with Docker Compose

```bash
make upb
```

The API will be available at `http://localhost:8021`

## API Documentation

- Swagger UI: `http://localhost:8021/docs`
- ReDoc: `http://localhost:8021/redoc`


## Limitations
- Maximum block range per request (/logs endpoint): 3000 blocks (depends on your RPС limits)
- It is important to have Archive node (for both chains)


## Development

### Running tests

Execute the full test suite:

```bash
make test
```

This will:
1. Build the test container
2. Run all tests with pytest
3. Clean up test containers

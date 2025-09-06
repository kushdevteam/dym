# Solana Narrative Scanner & MemeCoin Launcher

A comprehensive system for scanning social media platforms to identify emerging narratives and trending topics, then automatically generating and deploying meme coins on the Solana blockchain.

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   make setup
   # Edit .env file with your API keys
   ```

2. **Start Development Environment**
   ```bash
   make dev
   ```

3. **Access Services**
   - Dashboard: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
├── api/           # FastAPI backend
├── dashboard/     # Next.js frontend
├── ingest/        # Data ingestion services
├── nlp/           # NLP processing pipeline
├── bots/          # Telegram/Discord bots
├── onchain/       # Solana blockchain integration
├── ops/           # DevOps and monitoring
└── docker-compose.yml
```

## 🛠 Development Commands

- `make help` - Show available commands
- `make setup` - Initial project setup
- `make dev` - Start development environment
- `make build` - Build all containers
- `make logs` - Show all logs
- `make clean` - Clean up containers

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure:

- Database credentials
- Social media API keys (Reddit, Twitter, Telegram)
- AI/ML service tokens
- Solana configuration

## 📊 Features

### Phase 1 (MVP)
- [x] Monorepo structure
- [x] Database schema with pgvector
- [x] FastAPI skeleton with health endpoint
- [x] Next.js dashboard placeholder
- [ ] Reddit connector
- [ ] Telegram monitoring
- [ ] Basic NLP pipeline

### Phase 2
- [ ] Twitter/X integration
- [ ] TikTok trending analysis
- [ ] Narrative clustering
- [ ] Virality scoring
- [ ] Alert system

### Phase 3
- [ ] Coin ideation engine
- [ ] Solana token deployment
- [ ] Raydium LP creation
- [ ] Performance tracking

## 🔐 Security

- No hot private keys in logs
- API key management via environment variables
- Rate limiting and error handling
- Human approval required for token deployments

## 🧪 Testing

```bash
make test
```

## 📝 License

This project is for educational and research purposes.
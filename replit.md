# Solana Narrative Scanner & MemeCoin Launcher

## Overview

This project is a comprehensive system for scanning social media platforms to identify emerging narratives and trending topics, then automatically generating and deploying meme coins on the Solana blockchain. The system combines social media monitoring, natural language processing, sentiment analysis, and automated token deployment to capitalize on viral trends in real-time.

The platform ingests data from multiple sources (Twitter, Reddit, Telegram, TikTok, DEX feeds), processes it through NLP pipelines to identify trending narratives, ranks opportunities, and can automatically deploy SPL tokens with liquidity pools on Solana. It includes human oversight mechanisms and provides dashboards for monitoring and managing the entire pipeline.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**September 06, 2025**: Fixed critical Docker and database configuration issues:
- Updated docker-compose.yml API service to use Python uvicorn command instead of npm
- Fixed SQLAlchemy health check in main.py to properly use text() for raw queries
- Added pgvector indexes for similarity search on embedding and centroid columns
- Updated SQLAlchemy models to use PostgreSQL-specific types (JSONB, ARRAY)
- Removed unnecessary package.json from Python API service directory

**September 06, 2025** (Continued): Fixed critical Reddit connector issues:
- Replaced blocking Reddit ingestion with proper background tasks using BackgroundTasks
- Added async job tracking with unique job IDs and status endpoints (/ingest/reddit/jobs/{job_id})
- Fixed database query in /mentions endpoint to use SQLAlchemy text() bind parameters (:source, :since, :limit)
- Removed sys.path manipulation in favor of proper importlib dynamic module loading
- Implemented 202 Accepted responses for long-running ingestion tasks with progress tracking
- Added endpoints for listing and monitoring Reddit ingestion jobs

## System Architecture

### Monorepo Structure
The project follows a microservices-oriented monorepo pattern with distinct packages:
- `/ingest` - Data collection from social platforms
- `/nlp` - Natural language processing and narrative analysis
- `/api` - REST API and business logic layer
- `/dashboard` - Frontend monitoring interface
- `/bots` - Telegram/Discord notification bots
- `/onchain` - Solana blockchain interactions
- `/ops` - DevOps and infrastructure configurations

### Backend Architecture
**API Layer**: Built with FastAPI (Python) or NestJS (Node.js) providing RESTful endpoints for the frontend and external integrations. Handles authentication, rate limiting, and orchestrates the data pipeline.

**Data Processing Pipeline**: Asynchronous job processing using Celery with Redis as the message broker. Jobs handle data ingestion, NLP processing, narrative ranking, and blockchain deployments. Temporal workflow engine considered for complex multi-step processes.

**NLP Engine**: Python-based processing using spaCy for text preprocessing, sentence-transformers for embeddings, and BERTopic or custom clustering for narrative identification. Processes social media text to extract trending topics and sentiment.

### Frontend Architecture
**Dashboard**: Next.js application with Tailwind CSS and shadcn/ui components. Provides real-time monitoring of narratives, token performance, and system health. Uses Recharts for data visualization and analytics.

**Real-time Updates**: WebSocket connections for live data streaming to the dashboard, showing trending narratives and market movements as they happen.

### Data Storage Strategy
**Primary Database**: PostgreSQL with TimescaleDB extension for time-series data optimization. Stores raw social media mentions, processed narratives, token metadata, and trading data.

**Caching Layer**: Redis for high-frequency data access, API response caching, and session management. Also serves as the message queue for background jobs.

**Object Storage**: S3-compatible storage for media files, model artifacts, and data backups.

### Blockchain Integration
**Solana Integration**: Uses Solana web3.js for blockchain interactions, SPL-Token library for token creation, and Metaplex for NFT metadata. Anchor framework for any custom smart contracts.

**DEX Integration**: Raydium SDK for automated liquidity pool creation and management. Integrates with Dexscreener and Birdeye for market data.

**Wallet Management**: Secure key storage and transaction signing for automated token deployments with human approval workflows.

### Monitoring and Operations
**Observability**: Prometheus for metrics collection, Grafana for dashboards, and ELK stack for centralized logging. Tracks system performance, API usage, and business metrics.

**Deployment**: Docker containerization with docker-compose for local development. Production deployment likely on cloud platforms with Kubernetes or similar orchestration.

## External Dependencies

### Social Media APIs
- **Twitter/X API**: Official API or compliant firehose vendor for real-time tweet monitoring
- **Reddit API**: For accessing subreddit posts, comments, and engagement metrics
- **Telegram**: Telethon library for monitoring public channels (with proper consent)
- **TikTok**: Official analytics APIs for trending hashtags and viral content
- **Discord**: Discord.py for channel monitoring (stretch goal)

### Blockchain Services
- **Solana RPC**: Primary blockchain interaction endpoint
- **Metaplex**: NFT and token metadata standards
- **Raydium**: DEX protocol for liquidity pool creation
- **Dexscreener/Birdeye**: Market data and trading pair information

### AI/ML Services
- **Hugging Face**: Pre-trained language models and embeddings
- **OpenAI/Anthropic**: Advanced language models for narrative analysis (optional)
- **Custom NLP Stack**: spaCy, transformers, BERTopic for text processing

### Infrastructure Services
- **PostgreSQL**: Primary database with TimescaleDB extension
- **Redis**: Caching and message queuing
- **S3-compatible Storage**: File and artifact storage
- **Prometheus/Grafana**: Monitoring and alerting
- **Docker/Kubernetes**: Containerization and orchestration

### Development Tools
- **Celery/Temporal**: Workflow and job processing
- **FastAPI/NestJS**: API framework
- **Next.js**: Frontend framework
- **python-telegram-bot**: Bot framework for notifications
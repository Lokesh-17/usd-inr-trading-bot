# USD/INR Trading Bot - Full Stack 3-Tier Architecture

A modern full-stack web application for USD/INR currency trading with AI-powered chat assistance, built using a 3-tier architecture pattern.

## 🏗️ Architecture Overview

This application follows a **3-tier architecture** pattern:

### 1. **Presentation Tier (Frontend)**
- **Technology**: React 18 with Vite
- **UI Framework**: Tailwind CSS
- **Charts**: Recharts for data visualization
- **State Management**: React Context API
- **HTTP Client**: Axios

### 2. **Business Logic Tier (Backend)**
- **Technology**: FastAPI (Python)
- **API Documentation**: Automatic OpenAPI/Swagger
- **Authentication**: JWT-based (ready for implementation)
- **External APIs**: Alpha Vantage (Forex data), HuggingFace (AI chat)
- **Async Support**: Full async/await implementation

### 3. **Data Tier (Database)**
- **Technology**: PostgreSQL 15
- **ORM**: SQLAlchemy with Alembic migrations
- **Connection Pooling**: Built-in SQLAlchemy pooling
- **Data Persistence**: User portfolios, trades, chat history

## 🚀 Features

### Trading Features
- **Real-time USD/INR rates** from Alpha Vantage API
- **Virtual portfolio** with ₹1,00,000 starting balance
- **Buy/Sell USD** with real-time rate calculations
- **Interactive candlestick charts** with multiple timeframes
- **Trade history** with detailed transaction logs
- **Portfolio analytics** with P&L tracking

### AI Chat Assistant
- **HuggingFace integration** with SmolLM3-3B model
- **Context-aware responses** with current market data
- **Persistent chat history** stored in database
- **Fallback responses** when AI service is unavailable

### User Experience
- **Responsive design** works on desktop and mobile
- **Real-time updates** with automatic data refresh
- **Modern UI** with smooth animations and transitions
- **Error handling** with user-friendly messages

## 🛠️ Technology Stack

| Tier | Technology | Purpose |
|------|------------|---------|
| **Frontend** | React 18 + Vite | Modern UI framework |
| | Tailwind CSS | Utility-first styling |
| | Recharts | Data visualization |
| | React Router | Client-side routing |
| | Axios | HTTP client |
| **Backend** | FastAPI | High-performance API framework |
| | SQLAlchemy | Database ORM |
| | Pydantic | Data validation |
| | Alembic | Database migrations |
| | aiohttp | Async HTTP client |
| **Database** | PostgreSQL 15 | Relational database |
| **DevOps** | Docker Compose | Container orchestration |
| | Docker | Containerization |

## 📋 Prerequisites

- Docker and Docker Compose
- Alpha Vantage API key (free at [alphavantage.co](https://www.alphavantage.co/support/#api-key))
- HuggingFace API token (free at [huggingface.co](https://huggingface.co/settings/tokens))

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd usd-inr-trading-bot
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
# Alpha Vantage API (for forex data)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# HuggingFace API (for AI chat)
HF_TOKEN=your_huggingface_token_here
```

### 3. Start the Application
```bash
# Start all services (database, backend, frontend)
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (if you need direct access)

## 🗂️ Project Structure

```
usd-inr-trading-bot/
├── backend/                 # FastAPI Backend (Business Logic Tier)
│   ├── services/           # Business logic services
│   │   ├── forex_service.py    # Alpha Vantage integration
│   │   ├── ai_service.py       # HuggingFace AI integration
│   │   └── trading_service.py  # Trading business logic
│   ├── app.py              # FastAPI application
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container config
├── frontend/               # React Frontend (Presentation Tier)
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── services/       # API service layer
│   │   └── App.jsx         # Main app component
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Frontend container config
├── docker-compose.yml      # Multi-container orchestration
├── .env                    # Environment variables
└── README.md              # This file
```

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
# Start only the database
docker-compose up db

# Run migrations (if needed)
cd backend
alembic upgrade head
```

## 📊 API Endpoints

### User Management
- `POST /api/users` - Create new user
- `GET /api/users/{user_id}` - Get user details

### Portfolio Management
- `GET /api/users/{user_id}/portfolio` - Get portfolio
- `POST /api/users/{user_id}/portfolio/reset` - Reset portfolio

### Trading
- `POST /api/users/{user_id}/trades` - Execute trade
- `GET /api/users/{user_id}/trades` - Get trade history

### Forex Data
- `GET /api/forex/usd-inr` - Current exchange rate
- `GET /api/forex/chart-data` - Candlestick chart data

### AI Chat
- `POST /api/users/{user_id}/chat` - Send chat message
- `GET /api/users/{user_id}/chat` - Get chat history

## 🔒 Security Features

- **CORS middleware** configured for frontend communication
- **Input validation** using Pydantic schemas
- **SQL injection protection** via SQLAlchemy ORM
- **Environment variable** management for sensitive data
- **Error handling** without exposing internal details

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Performance Optimizations

- **Database connection pooling** for efficient DB connections
- **Async/await** throughout the backend for non-blocking operations
- **React lazy loading** for code splitting
- **API caching** for forex data (5-minute intervals)
- **Optimized Docker images** with multi-stage builds

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps db
   
   # View database logs
   docker-compose logs db
   ```

2. **API Rate Limits**
   - Alpha Vantage free tier: 5 requests/minute, 500/day
   - Consider upgrading for production use

3. **Frontend Build Issues**
   ```bash
   # Clear node modules and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Backend Import Errors**
   ```bash
   # Ensure all dependencies are installed
   cd backend
   pip install -r requirements.txt
   ```

## 🚀 Deployment

### Production Deployment
1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use managed PostgreSQL service
3. **API Keys**: Ensure production API keys are configured
4. **HTTPS**: Configure SSL/TLS certificates
5. **Monitoring**: Add logging and monitoring services

### Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Alpha Vantage** for providing forex data API
- **HuggingFace** for AI model hosting
- **FastAPI** for the excellent Python web framework
- **React** and **Tailwind CSS** for modern frontend development

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at http://localhost:8000/docs
- Review the troubleshooting section above

---

**Note**: This is a demo application for educational purposes. Do not use with real money or for actual trading decisions.
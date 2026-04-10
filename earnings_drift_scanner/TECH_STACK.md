# 🛠️ Earnings Drift Scanner - Technical Architecture

## Core Tech Stack

### Backend (Python)
- **FastAPI** - Modern, fast API framework
- **ib_insync** - IBKR data connection (you already know this!)
- **PostgreSQL** - Store historical patterns
- **Redis** - Cache real-time data
- **Celery** - Background job processing
- **SQLAlchemy** - Database ORM

### Frontend (React/Next.js)
- **Next.js 14** - Full-stack React framework
- **Tailwind CSS** - Rapid UI development
- **Chart.js** - Earnings drift visualizations
- **React Query** - Data fetching/caching
- **Vercel** - Hosting (free tier to start)

### AI/Analysis Layer
- **Claude Opus API** - Generate playbook narratives
- **Pandas/NumPy** - Statistical analysis
- **scipy.stats** - Event study calculations

### Infrastructure
- **DigitalOcean Droplet** - $20/mo to start
- **GitHub Actions** - CI/CD pipeline
- **Stripe** - Payment processing
- **SendGrid** - Transactional emails
- **Cloudflare** - CDN and DDoS protection

## Data Architecture

### Database Schema
```sql
-- Earnings events
CREATE TABLE earnings_events (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    earnings_date DATE,
    reported_time VARCHAR(10), -- BMO/AMC
    eps_actual DECIMAL,
    eps_estimate DECIMAL,
    revenue_actual DECIMAL,
    revenue_estimate DECIMAL
);

-- Price patterns
CREATE TABLE drift_patterns (
    id SERIAL PRIMARY KEY,
    earnings_event_id INT REFERENCES earnings_events(id),
    days_before INT,
    open_price DECIMAL,
    close_price DECIMAL,
    volume BIGINT,
    drift_percentage DECIMAL
);

-- User subscriptions
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(20),
    tier VARCHAR(20)
);
```

## API Endpoints

### Public
- `GET /api/earnings/upcoming` - Next 7 days earnings
- `GET /api/earnings/{symbol}/preview` - Free preview

### Authenticated
- `GET /api/earnings/{symbol}/analysis` - Full 12-quarter analysis
- `GET /api/earnings/{symbol}/playbook` - AI-generated playbook
- `GET /api/scanner/drift-opportunities` - Top drift candidates
- `POST /api/alerts/create` - Set price alerts

## Security
- JWT authentication
- Rate limiting (100 requests/min)
- API key rotation
- SSL/TLS everywhere
- Input sanitization

## Monitoring
- **Sentry** - Error tracking
- **PostHog** - Product analytics
- **Uptime Robot** - Availability monitoring
- **PagerDuty** - Critical alerts

## Scaling Plan

### Phase 1 (0-100 users)
- Single DigitalOcean droplet
- Shared PostgreSQL
- Manual processes

### Phase 2 (100-1000 users)
- Load balancer
- Separate database server
- Redis cluster
- CDN for static assets

### Phase 3 (1000+ users)
- Kubernetes cluster
- Read replicas
- Dedicated data pipeline
- 24/7 monitoring
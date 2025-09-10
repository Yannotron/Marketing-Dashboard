# Runbook: Reddit Dashboard 2

## Table of Contents

- [Local Development](#local-development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Security Operations](#security-operations)
- [Data Management](#data-management)
- [Key Rotation](#key-rotation)
- [Backup & Recovery](#backup--recovery)
- [Performance Optimization](#performance-optimization)
- [Emergency Procedures](#emergency-procedures)

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL (via Supabase)
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values:
# - REDDIT_CLIENT_ID
# - REDDIT_CLIENT_SECRET
# - REDDIT_USER_AGENT
# - SUPABASE_URL
# - SUPABASE_KEY
# - OPENAI_API_KEY

# Run the pipeline
python -m reddit_pipeline.run
```

### Web Setup

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your values:
# - VITE_SUPABASE_URL
# - VITE_SUPABASE_ANON_KEY

# Start development server
npm run dev
```

### Database Setup

```bash
# Apply database schema
psql -h your-supabase-host -U postgres -d postgres -f supabase/schema.sql

# Apply RLS policies
psql -h your-supabase-host -U postgres -d postgres -f supabase/policies.sql

# Seed with test data (optional)
psql -h your-supabase-host -U postgres -d postgres -f supabase/seed.sql
```

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest -q

# Run specific test file
pytest tests/test_ranking.py -v

# Run with coverage
pytest --cov=reddit_pipeline --cov-report=html

# Run linting
ruff check .
black --check .
mypy .
```

### Frontend Testing

```bash
cd web

# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Integration Testing

```bash
# Test full pipeline locally
cd backend
python -m reddit_pipeline.run --dry-run

# Test web app with real data
cd web
npm run build
npm run preview
```

## Deployment

### CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

- **Pull Requests**: Run linting, type checking, and tests
- **Main Branch**: Deploy to staging environment
- **Release Tags**: Deploy to production

### Environment Configuration

#### Development
- Uses local Supabase instance
- Mock data for testing
- Debug logging enabled

#### Staging
- Uses staging Supabase project
- Real data with limited scope
- Performance monitoring enabled

#### Production
- Uses production Supabase project
- Full data pipeline
- Comprehensive monitoring

### Deployment Steps

1. **Code Review**: All changes require PR review
2. **Automated Testing**: CI runs full test suite
3. **Security Scan**: Automated security checks
4. **Deployment**: Automated deployment to staging
5. **Smoke Tests**: Automated smoke tests
6. **Production Deploy**: Manual approval for production

## Monitoring & Troubleshooting

### Health Checks

#### Backend Health
```bash
# Check pipeline status
curl http://localhost:8000/health

# Check database connectivity
python -c "from reddit_pipeline.storage.supabase import get_client; print(get_client().table('posts').select('count').execute())"
```

#### Frontend Health
```bash
# Check if app is running
curl http://localhost:5173

# Check build status
npm run build
```

### Logging

#### Backend Logs
- **Location**: Structured JSON logs to stdout
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: JSON with timestamp, level, message, context

#### Frontend Logs
- **Browser Console**: Development errors
- **Network Tab**: API call failures
- **Lighthouse**: Performance metrics

### Common Issues

#### Backend Issues

**Pipeline Fails to Start**
```bash
# Check environment variables
python -c "from reddit_pipeline.config import settings; print(settings.dict())"

# Check database connection
python -c "from reddit_pipeline.storage.supabase import get_client; client = get_client(); print(client.table('posts').select('count').execute())"
```

**Rate Limiting**
- Check Reddit API rate limits
- Implement exponential backoff
- Monitor API usage

**Memory Issues**
- Check for memory leaks in data processing
- Monitor memory usage during large data operations
- Consider data chunking for large datasets

#### Frontend Issues

**Build Failures**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check TypeScript errors
npm run type-check
```

**Runtime Errors**
- Check browser console for errors
- Verify environment variables
- Check network connectivity to Supabase

### Performance Monitoring

#### Backend Metrics
- **Response Time**: API response times
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Resource Usage**: CPU, memory, disk usage

#### Frontend Metrics
- **Lighthouse Scores**: Performance, accessibility, SEO
- **Core Web Vitals**: LCP, FID, CLS
- **Bundle Size**: JavaScript bundle size
- **Load Time**: Page load times

## Security Operations

### PII Handling

All personal information is automatically stripped before external display:

```python
from reddit_pipeline.security import strip_pii_from_text

# Strip PII from text
clean_text = strip_pii_from_text("Contact me at user@example.com")
# Returns: "Contact me at [EMAIL_REDACTED]"
```

### Secret Management

#### Local Development
- Use `.env` files (never commit to git)
- Rotate keys regularly
- Use different keys for different environments

#### Production
- Use GitHub Secrets for CI/CD
- Use Supabase Vault for database secrets
- Implement key rotation schedule

### Security Monitoring

- **Dependency Scanning**: Automated vulnerability scanning
- **Code Analysis**: Static security analysis
- **Access Logs**: Monitor database access
- **Error Monitoring**: Track security-related errors

## Data Management

### Data Pipeline

1. **Data Collection**: Reddit API, HackerNews API, ProductHunt API
2. **Data Processing**: Deduplication, ranking, summarization
3. **Data Storage**: Supabase PostgreSQL
4. **Data Display**: React frontend

### Data Quality

#### Validation
- **Schema Validation**: Ensure data matches expected schema
- **Data Integrity**: Check for missing or invalid data
- **Consistency Checks**: Verify data consistency across sources

#### Monitoring
- **Data Freshness**: Monitor data age
- **Data Volume**: Track data collection rates
- **Data Quality**: Monitor error rates and data completeness

### Data Retention

- **Posts**: Retained for 90 days
- **Comments**: Retained for 30 days
- **Insights**: Retained indefinitely
- **Logs**: Retained for 30 days

## Key Rotation

### API Keys

#### Reddit API
1. Generate new client credentials
2. Update environment variables
3. Test with new credentials
4. Deploy to production
5. Revoke old credentials

#### OpenAI API
1. Generate new API key
2. Update environment variables
3. Test summarization functionality
4. Deploy to production
5. Revoke old key

#### Supabase Keys
1. Generate new anon key
2. Update environment variables
3. Test database connectivity
4. Deploy to production
5. Revoke old key

### Rotation Schedule

- **Monthly**: API keys
- **Quarterly**: Database credentials
- **Annually**: Master keys
- **As Needed**: Security incidents

## Backup & Recovery

### Database Backups

#### Automated Backups
- **Frequency**: Daily
- **Retention**: 30 days
- **Location**: Supabase managed backups

#### Manual Backups
```bash
# Create backup
pg_dump -h your-supabase-host -U postgres -d postgres > backup_$(date +%Y%m%d).sql

# Restore backup
psql -h your-supabase-host -U postgres -d postgres < backup_20240101.sql
```

### Code Backups

- **Git Repository**: Primary backup
- **GitHub**: Remote backup
- **Local**: Development machine backups

### Recovery Procedures

#### Database Recovery
1. Stop application
2. Restore from backup
3. Verify data integrity
4. Restart application
5. Monitor for issues

#### Code Recovery
1. Checkout from git
2. Restore environment variables
3. Install dependencies
4. Run tests
5. Deploy

## Performance Optimization

### Backend Optimization

#### Database
- **Indexing**: Ensure proper indexes on frequently queried columns
- **Query Optimization**: Use EXPLAIN ANALYZE for slow queries
- **Connection Pooling**: Optimize database connections

#### Data Processing
- **Caching**: Cache frequently accessed data
- **Batch Processing**: Process data in batches
- **Async Processing**: Use async/await for I/O operations

### Frontend Optimization

#### Bundle Optimization
- **Code Splitting**: Split code by routes
- **Tree Shaking**: Remove unused code
- **Minification**: Minify JavaScript and CSS

#### Runtime Optimization
- **Lazy Loading**: Load components on demand
- **Memoization**: Cache expensive calculations
- **Virtual Scrolling**: For large lists

### Monitoring

#### Performance Metrics
- **Response Time**: API response times
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Resource Usage**: CPU, memory, disk usage

#### Frontend Metrics
- **Lighthouse Scores**: Performance, accessibility, SEO
- **Core Web Vitals**: LCP, FID, CLS
- **Bundle Size**: JavaScript bundle size

## Emergency Procedures

### Incident Response

#### Severity Levels
- **P1 - Critical**: System down, data loss
- **P2 - High**: Major functionality affected
- **P3 - Medium**: Minor functionality affected
- **P4 - Low**: Cosmetic issues

#### Response Process
1. **Detection**: Monitor alerts and logs
2. **Assessment**: Determine severity and impact
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat/vulnerability
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve

### Rollback Procedures

#### Code Rollback
```bash
# Rollback to previous version
git checkout previous-commit-hash
npm run build
npm run deploy
```

#### Database Rollback
```bash
# Restore from backup
psql -h your-supabase-host -U postgres -d postgres < backup_previous.sql
```

### Communication

#### Internal
- **Slack**: #incidents channel
- **Email**: security@yourcompany.com
- **Phone**: Emergency contact list

#### External
- **Status Page**: Update status page
- **Users**: Email notification for P1/P2 issues
- **Public**: Coordinated disclosure for security issues

## Maintenance

### Regular Tasks

#### Daily
- Monitor system health
- Check error logs
- Verify data pipeline

#### Weekly
- Review performance metrics
- Check security alerts
- Update dependencies

#### Monthly
- Rotate API keys
- Review access logs
- Update documentation

#### Quarterly
- Security audit
- Performance review
- Disaster recovery test

### Documentation Updates

- **Code Changes**: Update inline documentation
- **API Changes**: Update API documentation
- **Process Changes**: Update runbook
- **Security Changes**: Update security policy

---

**Last Updated**: February 15, 2024  
**Next Review**: May 15, 2024  
**Maintainer**: [Your Name] - [email@yourcompany.com]
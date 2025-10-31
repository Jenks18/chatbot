# Data Collection & Privacy Documentation

## Overview
Your ToxicoGPT chatbot now collects comprehensive tracking and analytics data for every user interaction.

## Data Collected

### 1. **Session Information**
Stored in `sessions` table:

- **Session ID**: Unique identifier for each conversation session
- **IP Address**: Client's IP address (IPv4 or IPv6)
- **User Agent**: Browser and device information (e.g., "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...")
- **Country**: Detected from IP address
- **City**: Detected from IP address  
- **Region/State**: Detected from IP address
- **Timezone**: User's timezone
- **Latitude/Longitude**: Geographic coordinates
- **Started At**: When the session began
- **Last Active**: Last interaction timestamp

### 2. **Chat Log Information**
Stored in `chat_logs` table for EVERY query:

- **Question**: Exact text the user asked
- **Answer**: Complete AI response
- **IP Address**: User's IP for each query
- **User Agent**: Browser/device info
- **Model Used**: Which AI model answered (llama3.2:3b)
- **Response Time**: How long the AI took to respond (in milliseconds)
- **Timestamp**: Exact date/time of the query
- **Session ID**: Links to session data
- **Extra Metadata**: JSON field containing:
  - Geolocation data (country, city, ISP, etc.)
  - RAG usage (whether document retrieval was used)
  - Additional context as needed

### 3. **Geolocation Data (from IP)**
Retrieved in real-time using ip-api.com:

- **Country & Country Code**
- **City**
- **Region/State**  
- **Latitude & Longitude** (approximate)
- **Timezone**
- **ISP (Internet Service Provider)**
- **Organization**
- **AS Number** (Autonomous System)

## How It Works

### IP Geolocation Flow:
1. User makes a chat request
2. Backend captures IP address from request
3. Geolocation service queries ip-api.com (free API)
4. Location data returned and stored in database
5. Private/local IPs (127.0.0.1, 192.168.x.x, etc.) are marked as "Local"

### Data Storage:
- **PostgreSQL Database** stores all data persistently
- **JSON columns** store flexible metadata
- **Indexed fields** for fast searching by IP, country, city

## Privacy Considerations

### ⚠️ Important Notes:

1. **PII Collection**: This system collects Personally Identifiable Information (PII):
   - IP addresses can identify users/locations
   - Questions may contain personal information
   - Geolocation reveals approximate physical location

2. **Compliance Requirements**: Depending on your users' locations, you may need to comply with:
   - **GDPR** (Europe) - requires consent, right to deletion, data protection
   - **CCPA** (California) - requires privacy notices and opt-out options
   - **HIPAA** (if medical data) - requires strict security controls
   - **Other regional privacy laws**

3. **Recommended Actions**:
   - Add a **Privacy Policy** explaining data collection
   - Implement **user consent** mechanism
   - Add **data retention** policies (auto-delete old data)
   - Implement **data export/deletion** features
   - **Encrypt** sensitive data at rest
   - Use **HTTPS only** (encrypt data in transit)
   - Restrict **admin dashboard access** with authentication

## Admin Dashboard Access

View all collected data at: **http://localhost:3000/admin**

### What You Can See:
- ✅ Every question asked
- ✅ Every answer given
- ✅ IP addresses of all users
- ✅ Geographic locations (country, city, region)
- ✅ User timezones
- ✅ Browser/device information
- ✅ Response times and performance metrics
- ✅ Daily usage patterns
- ✅ ISP information

### Statistics Tracked:
- Total queries
- Unique sessions
- Average response time
- Daily query volume (7-day chart)
- Geographic distribution

## Database Schema

### Sessions Table:
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    region VARCHAR(100),
    timezone VARCHAR(50),
    latitude VARCHAR(20),
    longitude VARCHAR(20),
    started_at TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE,
    extra_metadata JSONB
);
```

### Chat Logs Table:
```sql
CREATE TABLE chat_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    model_used VARCHAR(50),
    response_time_ms INTEGER,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    extra_metadata JSONB
);
```

### Analytics View:
```sql
CREATE VIEW analytics_with_location AS
SELECT 
    cl.id, cl.question, cl.answer, cl.ip_address,
    s.country, s.city, s.region, s.timezone, s.latitude, s.longitude
FROM chat_logs cl
LEFT JOIN sessions s ON cl.session_id = s.session_id;
```

## Example Queries

### See all queries from a specific country:
```sql
SELECT cl.question, cl.answer, s.country, s.city 
FROM chat_logs cl
JOIN sessions s ON cl.session_id = s.session_id
WHERE s.country = 'United States';
```

### See most active locations:
```sql
SELECT s.country, s.city, COUNT(*) as query_count
FROM chat_logs cl
JOIN sessions s ON cl.session_id = s.session_id
GROUP BY s.country, s.city
ORDER BY query_count DESC;
```

### See all queries from a specific IP:
```sql
SELECT * FROM chat_logs WHERE ip_address = '123.456.789.0';
```

## Disabling Tracking

If you want to disable certain tracking features:

### Disable Geolocation:
In `backend/services/geo_service.py`:
```python
self.enabled = False  # Set to False
```

### Remove IP Logging:
In `backend/routers/chat.py`:
```python
ip_address=None,  # Instead of client_ip
```

### Clear Existing Data:
```sql
-- Clear all logs
TRUNCATE TABLE chat_logs CASCADE;
TRUNCATE TABLE sessions CASCADE;
```

## Security Recommendations

1. **Add Authentication**: Protect admin dashboard with login
2. **Use Environment Variables**: Don't hardcode database passwords
3. **Enable SSL**: Use HTTPS for production
4. **Restrict Database Access**: Firewall rules, strong passwords
5. **Regular Backups**: Backup database regularly
6. **Audit Logs**: Track who accesses admin dashboard
7. **Data Anonymization**: Consider anonymizing IPs after certain period
8. **Rate Limiting**: Prevent abuse by limiting requests per IP

## Legal Disclaimer

**This is a development system. Before deploying to production with real users:**
- Consult with legal counsel about privacy requirements
- Implement proper consent mechanisms
- Add privacy policy and terms of service
- Consider data protection impact assessments (DPIA)
- Implement user data rights (access, deletion, portability)

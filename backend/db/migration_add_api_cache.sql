-- Migration: Add API Cache table
-- Purpose: Cache responses from external APIs (RxNorm, FDA, PubChem, OpenFDA, PubMed)
-- Date: 2025-11-04

CREATE TABLE IF NOT EXISTS api_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    api_source VARCHAR(50) NOT NULL,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_cache_key ON api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires ON api_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_api_cache_source ON api_cache(api_source);

-- Comments
COMMENT ON TABLE api_cache IS 'Caches responses from external drug APIs to reduce API calls and improve performance';
COMMENT ON COLUMN api_cache.cache_key IS 'Unique identifier for cached data (e.g., rxnorm_acetaminophen)';
COMMENT ON COLUMN api_cache.api_source IS 'Source API: rxnorm, fda, pubchem, openfda, pubmed';
COMMENT ON COLUMN api_cache.response_data IS 'JSON response from the API';
COMMENT ON COLUMN api_cache.expires_at IS 'When this cache entry expires and should be refreshed';

"""
Health check endpoint with comprehensive system status
"""
from typing import Dict, Any
import psutil
import os
from datetime import datetime


class HealthCheck:
    """Comprehensive health check utility"""
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """
        Get comprehensive system health status
        
        Returns:
            Health status dictionary
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check database connectivity
        health_status["checks"]["database"] = HealthCheck._check_database()
        
        # Check API keys
        health_status["checks"]["api_keys"] = HealthCheck._check_api_keys()
        
        # Check system resources
        health_status["checks"]["system"] = HealthCheck._check_system_resources()
        
        # Determine overall status
        if any(check["status"] == "unhealthy" for check in health_status["checks"].values()):
            health_status["status"] = "unhealthy"
        elif any(check["status"] == "degraded" for check in health_status["checks"].values()):
            health_status["status"] = "degraded"
        
        return health_status
    
    @staticmethod
    def _check_database() -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from backend.db.database import SessionLocal, DATABASE_URL
            
            db = SessionLocal()
            # Try a simple query
            db.execute("SELECT 1")
            db.close()
            
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "connection_string": DATABASE_URL[:30] + "..." if len(DATABASE_URL) > 30 else "configured"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
    
    @staticmethod
    def _check_api_keys() -> Dict[str, Any]:
        """Check if required API keys are configured"""
        groq_key = os.getenv("GROQ_API_KEY")
        
        keys_status = {
            "groq": "configured" if groq_key else "missing"
        }
        
        if not groq_key:
            return {
                "status": "unhealthy",
                "message": "GROQ_API_KEY not configured",
                "keys": keys_status
            }
        
        return {
            "status": "healthy",
            "message": "All required API keys configured",
            "keys": keys_status
        }
    
    @staticmethod
    def _check_system_resources() -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            warnings = []
            
            if cpu_percent > 90:
                status = "degraded"
                warnings.append("High CPU usage")
            
            if memory.percent > 90:
                status = "degraded"
                warnings.append("High memory usage")
            
            if disk.percent > 90:
                status = "degraded"
                warnings.append("Low disk space")
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "warnings": warnings if warnings else None
            }
        except Exception as e:
            return {
                "status": "unknown",
                "message": f"Could not check system resources: {str(e)}"
            }


# Global health check instance
health_checker = HealthCheck()

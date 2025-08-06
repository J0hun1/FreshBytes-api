# FreshBytes API - Logging & Monitoring Guide

## 🎯 **Overview**

This guide explains how to use the comprehensive logging and monitoring system implemented in the FreshBytes API. The system provides structured logging for security events, business transactions, and application monitoring.

## 📊 **What We've Implemented**

### ✅ **1. Structured Logging Configuration**
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR
- **Separate log files**: Main app, errors, security, business events
- **Detailed formatters**: Include timestamp, module, function, line numbers
- **Rotating file handlers**: Automatic log rotation

### ✅ **2. Health Check Endpoints**
- **Comprehensive health check** (`/api/health/`): Database, cache, system resources
- **Simple health check** (`/api/health/simple/`): For load balancers
- **Real-time monitoring**: CPU, memory, disk usage

### ✅ **3. Critical View Logging**
- **Authentication**: Login/logout security tracking
- **User Management**: Enable/disable audit trails
- **Business Transactions**: Payment and order processing

## 🔧 **How to Use the Logging System**

### **A. Viewing Logs**

#### **1. Main Application Logs**
```bash
# View main application logs
tail -f logs/freshbytes.log

# Search for specific events
grep "LOGIN_SUCCESS" logs/freshbytes.log
grep "USER_ENABLED" logs/freshbytes.log
```

#### **2. Security Logs**
```bash
# View security events
tail -f logs/security.log

# Search for failed login attempts
grep "LOGIN_FAILED" logs/security.log
```

#### **3. Business Event Logs**
```bash
# View business transactions
tail -f logs/business.log

# Search for checkout events
grep "CHECKOUT_SUCCESS" logs/business.log
```

#### **4. Error Logs**
```bash
# View error logs
tail -f logs/error.log

# Search for specific errors
grep "ERROR" logs/error.log
```

### **B. Health Monitoring**

#### **1. Check System Health**
```bash
# Comprehensive health check
curl http://localhost:8000/api/health/

# Simple health check (for load balancers)
curl http://localhost:8000/api/health/simple/
```

#### **2. Monitor System Resources**
The health check provides real-time information about:
- **Database connectivity**
- **Cache functionality**
- **CPU usage**
- **Memory usage**
- **Disk space**

### **C. Testing the Logging System**

#### **1. Run Logging Tests**
```bash
cd FreshBytes
python manage.py test api.tests.test_logging -v 2
```

#### **2. Manual Testing**
```bash
# Test login logging
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "adminpass123"}'

# Test logout logging
curl -X POST http://localhost:8000/api/logout/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## 📈 **What Gets Logged**

### **1. Security Events**
- ✅ **Login attempts** (successful and failed)
- ✅ **Logout events**
- ✅ **User enable/disable actions**
- ✅ **IP addresses and user agents**

### **2. Business Events**
- ✅ **Checkout attempts and results**
- ✅ **Payment status changes**
- ✅ **Order processing**
- ✅ **User management actions**

### **3. System Events**
- ✅ **Health check requests**
- ✅ **Database operations**
- ✅ **Error occurrences**
- ✅ **Performance metrics**

## 🔍 **Log Analysis Examples**

### **A. Security Monitoring**

#### **Find Failed Login Attempts**
```bash
grep "LOGIN_FAILED" logs/security.log | tail -10
```

#### **Track User Sessions**
```bash
grep "LOGOUT_SUCCESS" logs/security.log | tail -10
```

#### **Monitor Admin Actions**
```bash
grep "USER_ENABLED\|USER_DISABLED" logs/business.log | tail -10
```

### **B. Business Intelligence**

#### **Track Checkout Success Rate**
```bash
# Count successful checkouts
grep "CHECKOUT_SUCCESS" logs/business.log | wc -l

# Count failed checkouts
grep "CHECKOUT_FAILED" logs/business.log | wc -l
```

#### **Monitor Payment Processing**
```bash
grep "PAYMENT_STATUS_CHANGED" logs/business.log | tail -10
```

### **C. Performance Monitoring**

#### **Check System Health**
```bash
# Get current system status
curl -s http://localhost:8000/api/health/ | python -m json.tool
```

#### **Monitor Error Rates**
```bash
# Count errors in the last hour
grep "$(date '+%Y-%m-%d %H')" logs/error.log | wc -l
```

## 🛠 **Customization Options**

### **A. Adding Logging to New Views**

```python
import logging
from ..utils.logging_utils import log_business_event, log_security_event

logger = logging.getLogger(__name__)

class YourViewSet(viewsets.ModelViewSet):
    def your_action(self, request):
        try:
            # Your business logic here
            
            # Log the event
            log_business_event(
                event_type="YOUR_EVENT_TYPE",
                user_id=str(request.user.user_id),
                details={"key": "value"}
            )
            
            logger.info(f"Action completed for user: {request.user.user_name}")
            
        except Exception as e:
            logger.error(f"Error in action: {str(e)}")
            raise
```

### **B. Custom Log Levels**

```python
# Debug level for development
logger.debug("Detailed debug information")

# Info level for general events
logger.info("General information")

# Warning level for potential issues
logger.warning("Warning message")

# Error level for errors
logger.error("Error message")
```

## 📊 **Monitoring Dashboard Ideas**

### **A. Real-time Monitoring**
- **Active users**: Count current sessions
- **Error rates**: Monitor error frequency
- **Response times**: Track API performance
- **Business metrics**: Track transactions

### **B. Alerting**
- **High error rates**: Alert when errors spike
- **Failed logins**: Alert on suspicious activity
- **System resources**: Alert when resources are low
- **Business events**: Alert on critical transactions

## 🚀 **Production Considerations**

### **A. Log Rotation**
- Logs are automatically rotated when they reach 10MB
- Old logs are compressed and archived
- Log retention is configurable

### **B. Security**
- Sensitive data is not logged (passwords, tokens)
- IP addresses are logged for security monitoring
- User agents are logged for debugging

### **C. Performance**
- Logging is asynchronous to avoid blocking
- File I/O is optimized for production
- Log levels can be adjusted per environment

## 📝 **Best Practices**

### **1. Log Levels**
- **DEBUG**: Detailed information for development
- **INFO**: General application events
- **WARNING**: Potential issues that don't stop execution
- **ERROR**: Errors that need attention

### **2. Security**
- Never log passwords or sensitive tokens
- Always log security events (login, logout, admin actions)
- Monitor failed login attempts

### **3. Business Events**
- Log all financial transactions
- Track user actions that affect business
- Monitor system health regularly

### **4. Maintenance**
- Regularly check log file sizes
- Archive old logs
- Monitor disk space usage
- Review error logs daily

## 🎯 **Next Steps**

1. **Set up log monitoring**: Configure alerts for critical events
2. **Create dashboards**: Visualize log data for insights
3. **Automate analysis**: Set up automated log analysis
4. **Scale logging**: Consider centralized logging for multiple servers

This logging system provides the foundation for comprehensive monitoring and debugging of your FreshBytes API! 
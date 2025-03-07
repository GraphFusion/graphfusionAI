# Module 5: Real-World Applications

## Learning Objectives
By the end of this module, you will:
- Understand real-world agent deployment patterns
- Master performance optimization techniques
- Implement security best practices
- Build production-ready agent systems

## 1. Case Study: Intelligent Customer Service System

### System Architecture
```python
from graphfusionai import (
    Agent, Role, KnowledgeGraph, Memory,
    CommunicationBus, StateManager
)
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta

class CustomerServiceAgent(Agent):
    def __init__(
        self,
        name: str,
        role: Role,
        knowledge_base: KnowledgeGraph,
        state_file: str
    ):
        super().__init__(name=name, role=role)
        self.knowledge_base = knowledge_base
        self.memory = Memory()
        self.state_manager = StateManager(state_file)
        self.conversation_history = []

    async def handle_customer_query(
        self,
        query: str,
        customer_id: str
    ) -> Dict[str, Any]:
        # Log interaction
        interaction = {
            "timestamp": datetime.now(),
            "customer_id": customer_id,
            "query": query
        }
        self.conversation_history.append(interaction)

        # Check customer history
        customer_context = await self._get_customer_context(customer_id)
        
        # Process query with context
        response = await self._generate_response(query, customer_context)
        
        # Update customer context
        await self._update_customer_context(customer_id, query, response)
        
        return {
            "response": response,
            "context": customer_context
        }

    async def _get_customer_context(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        # Try short-term memory first
        context = await self.memory.retrieve(f"customer_{customer_id}")
        if context:
            return context

        # Check knowledge base
        query = {
            "type": "customer_data",
            "customer_id": customer_id
        }
        return await self.knowledge_base.query(query)

    async def _generate_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        # Implement response generation logic
        pass

    async def _update_customer_context(
        self,
        customer_id: str,
        query: str,
        response: str
    ):
        context = {
            "last_interaction": datetime.now(),
            "recent_queries": query,
            "last_response": response
        }
        await self.memory.store(
            f"customer_{customer_id}",
            context,
            expiry=timedelta(hours=24)
        )
```

## 2. Performance Optimization

### Caching and Resource Management
```python
from functools import lru_cache
from typing import Optional
import asyncio

class OptimizedAgent(Agent):
    def __init__(self, name: str, role: Role, cache_size: int = 1000):
        super().__init__(name=name, role=role)
        self.cache_size = cache_size
        self._response_cache = {}
        self._resource_semaphore = asyncio.Semaphore(10)

    @lru_cache(maxsize=1000)
    async def cached_operation(self, input_data: str) -> Any:
        # Expensive operation with caching
        result = await self._process_data(input_data)
        return result

    async def process_with_resources(self, task: Dict[str, Any]) -> Any:
        async with self._resource_semaphore:
            return await self._process_task(task)

    def clear_cache(self):
        self._response_cache.clear()
        self.cached_operation.cache_clear()

    async def _process_data(self, input_data: str) -> Any:
        # Implement actual data processing
        pass
```

## 3. Security Best Practices

### Secure Agent Implementation
```python
import hashlib
import secrets
from cryptography.fernet import Fernet
from typing import Optional

class SecureAgent(Agent):
    def __init__(
        self,
        name: str,
        role: Role,
        encryption_key: bytes
    ):
        super().__init__(name=name, role=role)
        self.cipher_suite = Fernet(encryption_key)
        self._api_keys = {}
        self._access_tokens = {}

    async def authenticate_request(
        self,
        request: Dict[str, Any]
    ) -> bool:
        token = request.get("access_token")
        if not token:
            return False

        # Verify token
        return self._verify_token(token)

    def encrypt_sensitive_data(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        return self.cipher_suite.decrypt(
            encrypted_data.encode()
        ).decode()

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _verify_token(self, token: str) -> bool:
        return token in self._access_tokens

    async def rotate_api_keys(self):
        for service in self._api_keys:
            self._api_keys[service] = self._generate_token()
```

## 4. Production Deployment

### Monitoring and Logging
```python
import logging
from datetime import datetime
from typing import Optional

class ProductionAgent(Agent):
    def __init__(
        self,
        name: str,
        role: Role,
        log_file: str
    ):
        super().__init__(name=name, role=role)
        self._setup_logging(log_file)
        self.metrics = {
            "requests_processed": 0,
            "errors": 0,
            "average_response_time": 0
        }

    def _setup_logging(self, log_file: str):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)

    async def process_task(self, task: Dict[str, Any]) -> Any:
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Processing task: {task['type']}")
            result = await super().process_task(task)
            self.metrics["requests_processed"] += 1
            
            # Update average response time
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error processing task: {str(e)}")
            raise

    def _update_average_response_time(self, new_time: float):
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["requests_processed"]
        
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + new_time) / total_requests
        )

    def get_health_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.metrics["errors"] < 100 else "degraded",
            "metrics": self.metrics,
            "memory_usage": self._get_memory_usage(),
            "uptime": self._get_uptime()
        }
```

## Exercise: Build a Production-Ready Agent System

Create a complete production system that includes:
1. A main agent service with proper error handling
2. Monitoring and alerting system
3. Performance optimization with caching
4. Secure data handling
5. Comprehensive logging
6. Health checks and metrics
7. Deployment configuration

## Best Practices Checklist
- [ ] Implement proper error handling
- [ ] Add comprehensive logging
- [ ] Set up monitoring and alerting
- [ ] Implement security measures
- [ ] Add performance optimization
- [ ] Create deployment documentation
- [ ] Set up backup and recovery
- [ ] Implement health checks
- [ ] Add metrics collection
- [ ] Create maintenance procedures

## Next Steps
- Review the [exercise solution](exercise_solution.py)
- Explore the complete [API Reference](../../api_reference.md)
- Join our [Community Forum](https://community.graphfusion.ai)
- Check out real-world case studies in our [Blog](https://blog.graphfusion.ai)

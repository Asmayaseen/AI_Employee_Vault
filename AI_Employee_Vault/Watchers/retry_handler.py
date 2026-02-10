#!/usr/bin/env python3
"""
Retry Handler (Gold Tier - Error Recovery)

Provides exponential backoff retry logic for all watcher and MCP operations.
Implements Section 7.2 of the hackathon architecture.

Usage:
    @with_retry(max_attempts=3, base_delay=1.0, max_delay=60.0)
    def my_fragile_function():
        ...

    # Or use the RetryExecutor directly
    executor = RetryExecutor(max_attempts=5)
    result = executor.execute(my_function, arg1, arg2)
"""

import time
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional, Type, Tuple
from datetime import datetime

logger = logging.getLogger('RetryHandler')


class TransientError(Exception):
    """Errors that may succeed on retry (network, timeout, rate-limit)."""
    pass


class PermanentError(Exception):
    """Errors that will not benefit from retrying (auth, bad data)."""
    pass


class RetryExhaustedError(Exception):
    """All retry attempts have been exhausted."""
    def __init__(self, original_error: Exception, attempts: int):
        self.original_error = original_error
        self.attempts = attempts
        super().__init__(
            f"All {attempts} attempts exhausted. Last error: {original_error}"
        )


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        TransientError, ConnectionError, TimeoutError, OSError
    ),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        retryable_exceptions: Exception types that trigger retry
        on_retry: Optional callback(attempt, error, delay) on each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_error = e
                    if attempt == max_attempts:
                        logger.error(
                            f"[{func.__name__}] All {max_attempts} attempts failed: {e}"
                        )
                        raise RetryExhaustedError(e, max_attempts)

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"[{func.__name__}] Attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.1f}s"
                    )

                    if on_retry:
                        on_retry(attempt, e, delay)

                    time.sleep(delay)

                except Exception as e:
                    # Non-retryable: fail immediately
                    logger.error(f"[{func.__name__}] Permanent error: {e}")
                    raise

            raise RetryExhaustedError(last_error, max_attempts)

        return wrapper
    return decorator


class RetryExecutor:
    """
    Programmatic retry executor for dynamic use.

    Example:
        executor = RetryExecutor(max_attempts=3)
        result = executor.execute(risky_api_call, endpoint, data)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        retryable_exceptions: Tuple[Type[Exception], ...] = (
            TransientError, ConnectionError, TimeoutError, OSError
        )
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retryable_exceptions = retryable_exceptions
        self.history = []

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                self.history.append({
                    'function': func.__name__,
                    'attempt': attempt,
                    'success': True,
                    'duration': time.time() - start,
                    'timestamp': datetime.now().isoformat(),
                })
                return result

            except self.retryable_exceptions as e:
                last_error = e
                duration = time.time() - start
                self.history.append({
                    'function': func.__name__,
                    'attempt': attempt,
                    'success': False,
                    'error': str(e),
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                })

                if attempt == self.max_attempts:
                    raise RetryExhaustedError(e, self.max_attempts)

                delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                logger.warning(
                    f"[{func.__name__}] Attempt {attempt}/{self.max_attempts}: {e}. "
                    f"Retry in {delay:.1f}s"
                )
                time.sleep(delay)

            except Exception as e:
                self.history.append({
                    'function': func.__name__,
                    'attempt': attempt,
                    'success': False,
                    'error': str(e),
                    'permanent': True,
                    'duration': time.time() - start,
                    'timestamp': datetime.now().isoformat(),
                })
                raise

        raise RetryExhaustedError(last_error, self.max_attempts)

    def get_stats(self) -> dict:
        """Get retry statistics."""
        total = len(self.history)
        successes = sum(1 for h in self.history if h['success'])
        failures = total - successes
        return {
            'total_attempts': total,
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / total * 100) if total > 0 else 0,
        }

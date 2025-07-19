"""
Logging configuration for the proofreading application.
"""

import logging
import logging.config
import sys
from typing import Any, Dict

from pydantic import BaseSettings


class LogSettings(BaseSettings):
    """Logging settings configuration."""
    
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    log_file: str = "app.log"
    
    class Config:
        env_prefix = "LOG_"


def get_logging_config(settings: LogSettings) -> Dict[str, Any]:
    """Get logging configuration based on settings."""
    
    formatters = {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "text": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    }
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": formatters.get(settings.log_format, formatters["text"])
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": "default",
                "filename": settings.log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # root logger
                "level": settings.log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    }


def setup_logging(settings: LogSettings) -> None:
    """Setup logging configuration."""
    config = get_logging_config(settings)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
""" 
Configuration loader - reads from environment variables.
All config values are read-only at runtime.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from dataclasses import dataclass
from os import getenv

@dataclass(frozen=True) # immutable after creation
class BMKGConfig:
    base_url: str
    timeout_sec: int
    user_agent: str

@dataclass(frozen=True)
class MinIOConfig:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_raw: str
    bucket_staged: str
    bucket_marts: str

@dataclass(frozen=True)
class Config:
    bmkg: BMKGConfig
    minio: MinIOConfig
    log_level: str
    timezone: str

def load_config() -> Config:
    """ Factroy: build config from environment variables. """
    bmkg_cfg = BMKGConfig(
        base_url=getenv("BMKG_BASE_URL", "https://api.bmkg.go.id"),
        timeout_sec=int(getenv("BMKG_TIMEOUT_SEC", "15")),
        user_agent=getenv("BMKG_USER_AGENT","bmkg-data-platform/0.1.0")
    )
    minio_cfg = MinIOConfig(
        endpoint=getenv("MINIO_ENDPOINT"),
        access_key=getenv("MINIO_ROOT_USER"),
        secret_key=getenv("MINIO_ROOT_PASSWORD"),
        bucket_raw=getenv("MINIO_BUCKET_RAW"),
        bucket_staged=getenv("MINIO_BUCKET_STAGED"),
        bucket_marts=getenv("MINIO_BUCKET_MARTS")
    )
    return Config(
        bmkg=bmkg_cfg,
        minio=minio_cfg,
        log_level=getenv("LOG_LEVEL","INFO"),
        timezone=getenv("TZ","Asia/Jakarta")
    )

    # def get_local_now() -> datetime:
    #     """ Get current time in configured timezone. """
    #     return datetime.now(ZoneInfo(timezone))

# Singleton - instantiated once, imported everywhere
config = load_config()
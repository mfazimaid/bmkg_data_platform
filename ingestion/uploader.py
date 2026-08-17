"""
MinIO (S3-compatible) uploader for raw BMKG payloads.
provides raw JSON upload with ADM4-based partitioning.
"""
import io
import logging
from datetime import datetime
from typing import Optional

from minio import Minio

from .config import config
from .models import BMKGForecast, Location

logger = logging.getLogger(__name__)

class MinIOUploader:
    """
    Uploads BMKG payloads to MinIO object storage.

    Object key pattern:
        {bucket}/year=YYYY/month=MM/day/DD/adm1=XX/adm4=XX.XX.XX.XXXX/timestamp.json
    
    Partitioning benefits:
    - Spark can prune by date (year/month/day)
    - Spark can prune by province
    - Spark can filter by specific village (adm4)
    """

    def __init__(self) -> None:
        self._client: Optional[Minio] = None 
    
    @property
    def client(self) -> Minio:
        """ Lazy-init MinIO client."""
        if self._client is None:
            self._client = Minio(
                endpoint=config.minio.endpoint,
                access_key=config.minio.access_key,
                secret_key=config.minio.secret_key,
                secure=False # local MinIO, no TLS
            )
        return self._client 

    def _make_key(
        self,
        location: Location,
        extension: str = "json"
    ) -> str:
        """ 
        Build object key with date + ADM4 partitioning
        
        Args: 
            location: Location model from BMKGForecast.
            extension: File extension (default: JSON).

        Returns:
            Object key string like:
                year=2026/month=08/day=16/adm1=31/adm4=31.71.03.1001/20260816T20000.json
        """
        # extract timestamps
        dt = datetime.utcnow()

        # Get ADM codes safety
        adm1 = location.adm1 or "XX"
        adm4 = location.adm4 or "unknown"

        # Build key with hierarchical partitioning
        return (
            f"year={dt.year}/month={dt.month:02d}/day={dt.day:02d}"
            f"/adm1={adm1}/adm4={adm4}"
            f"/{dt.strftime('%Y%m%dT%H%M%S')}.{extension}"
        )

    def upload_json(
        self,
        forecast: BMKGForecast
    ) -> str:
        """ 
        Upload normalized JSON forecast to weather-raw bucket.

        Args:
            forecast: Parsed BMKGForecast model from BMKG API.

        Returns:
            Object key in MinIO.
        """
        if not forecast.lokasi:
            raise ValueError("Forecast has no-location data")
        
        location = forecast.lokasi
        adm4 = location.adm4 or "unknown"
        key = self._make_key(location, "json")

        # Serialize forecast to JSON bytes
        data = forecast.model_dump_json().encode("utf-8")

        self.client.put_object(
            bucket_name=config.minio.bucket_raw,
            object_name=key,
            data=io.BytesIO(data),
            length=len(data),
            content_type="application/json",
            metadata={
                "adm1": location.adm1 or "",
                "adm4": adm4,
                "provinsi": location.provinsi or "",
                "kotkab": location.kotkab or "",
                "kecamatan": location.kecamatan or "",
                "source": "bmkg",
                "ingested_at": datetime.utcnow().isoformat()
            }
        )
        logger.info("Uploaded JSON: %s%s (adm4=%s)", config.minio.bucket_raw, key, adm4)
        return key

    def __enter__(self) -> "MinIOUploader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """ Minio client doesnt need explicit close (stateless). """
        self._client = None


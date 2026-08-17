"""
BMKG Ingestion CLI entrypoint.

Usage:
    python -m bmkg fetch                        # fetch sample villages
    python -m bmkg fetch --adm4 31.71.03.1001   # fetch specific village
    python -m bmkg list                         # list sample villages
    python -m bmkg test                         # test with local fixture
"""
import argparse
import logging
import sys
import time
from pathlib import Path

from .client import BMKGClient
from .config import config
from .parser import get_sample_villages, parse_bmkg_json
from .uploader import MinIOUploader

# Structured Logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

def cmd_list(args) -> None:
    """List all sample villages with ADM4 codes."""
    villages = get_sample_villages()
    print(f"{'ADM4':<20} {'Province':<15} {'Kota/kab':<25} {'Kecamatan':<15} {'URL'}")
    print("-" * 100)
    for v in villages:
        print(f"{v.adm4:<20} {v.provinsi:<15} {v.kotkab:<25} {v.kecamatan:<15} {v.api_url}")
    
def cmd_fetch(args) -> None:
    """ Fetch BMKG data for specified village (or all sample villages). """
    villages = get_sample_villages()

    # Filter if specific province requested
    if args.adm4:
        villages = [v for v in villages if v.adm4 == args.adm4]
        if not villages:
            logger.error("ADM4 '%s' not found in sample list.", args.adm4)
            sys.exit(1)

    total = len(villages)
    logger.info("Fetching %d location(s)", total)

    success_count = 0
    error_count = 0

    with BMKGClient() as client, MinIOUploader() as uploader:
        for i, village in enumerate(villages, 1):
            try:
                logger.info(
                    "[%d/%d] Fetching: %s, %s (%s)",
                    i, total,
                    village.adm4_short,
                    village.kecamatan,
                    village.adm4
                )

                #1. Fetch JSON from BMKG API
                json_data = client.fetch_json(village.api_url)

                # 2. Parse to Pydantic model
                forecast = parse_bmkg_json(json_data)

                # 3. Upload to MinIO
                key = uploader.upload_json(forecast)
                
                success_count += 1
                cuaca_count = len(forecast.data[0].cuaca) if forecast.data else 0
                logger.info(
                    "✓ %s done - %d cuaca entries uploaded",
                    village.adm4_short,
                    cuaca_count
                )

                # Rate limit protection: sleep 1 second between requests
                if i < total:
                    time.sleep(1)

            except Exception as exc: # noqa: BLE001
                error_count += 1
                logger.error("✗ %s failed: %s", village.adm4, exc)
                if args.fail_fast:
                    logger.info("Stopping due to --fail-fast")
                    break

    logger.info("Done, Success: %d, Errors: %d", success_count, error_count)
    sys.exit (0 if error_count == 0 else 1)

def cmd_test(args) -> None:
    """ Test parser with local fixture (no network required). """
    fixture_path = Path(__file__).parent / "fixtures" / "sample_bmkg.json"

    if not fixture_path.exists():
        logger.error("Fixture not found: %s", fixture_path)
        logger.error("Run: curl -s 'https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.71.03.1001' > ingestion/fixture/sample_bmkg.json")
        sys.exit(1)

    import json
    with open(fixture_path) as f:
        data = json.load(f)

    logger.info("Testing parser with: %s", fixture_path)
    forecast = parse_bmkg_json(data)

    if forecast.lokasi:
        loc = forecast.lokasi
        logger.info("✓ Province: %s", loc.provinsi)
        logger.info("✓ Kota/Kab: %s", loc.kotkab)
        logger.info("✓ Kecamatan: %s", loc.kecamatan)
        logger.info("✓ ADM4: %s", loc.adm4)

    if forecast.data:
        all_cuaca = []
        for block in forecast.data:
            if block.cuaca:
                for day_group in block.cuaca:
                    all_cuaca.extend(day_group)
        logger.info("✓ Total cuaca entries across all days: %d", len(all_cuaca))
        
        if all_cuaca:
            first = all_cuaca[0]
            logger.info(
                "Sample: t=%s°C, hu=%s%%, weather=%s",
                first.t,
                first.hu,
                first.weather_desc
            )

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bmkg",
        description="BMKG Weather Data Ingestion Tool (JSON API)"
    )
    subparsers = parser.add_subparsers(required=True)

    # 'bmkg list'
    list_parser = subparsers.add_parser("list", help="List sample village endpoints")
    list_parser.set_defaults(func=cmd_list)

    # 'bmkg test'
    test_parser = subparsers.add_parser("test", help="Test parser with local fixture(no network)")
    test_parser.set_defaults(func=cmd_test)
    # 'bmkg fetch'
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and ingest BMKG forecast data")
    fetch_parser.add_argument(
        "--adm4",
        help="ADM4 village code (e.g. 31.71.03.1001)"
    )
    fetch_parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop on first error (default: continue)"
    )
    fetch_parser.set_defaults(func=cmd_fetch)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
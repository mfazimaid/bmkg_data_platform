"""
JSON parser for BMKG weather forecast data.
API returns JSON.
"""

import logging
from datetime import datetime
from typing import Optional, List

from .models import (BMKGForecast, VillageIndex)

logger = logging.getLogger(__name__)


class BMKGParseError(Exception):
    """ Raised When JSON cannot be parsed or validated. """
    pass

def parse_bmkg_json(json_data: dict) -> BMKGForecast:
    """
    Parse raw BMKG JSON dict into BMKGForecast Pydantic model.

    Args:
        json_data: Dict from response.json()

    Returns:
        Validated BMKGForecast object.

    Raises:
        BMKGParseError: If JSON is invalid or missing required fields.
    """
    if not isinstance(json_data, dict):
        raise BMKGParseError(f"Expected dict, got {type(json_data)}")

    if "lokasi" not in json_data and "data" not in json_data:
        raise BMKGParseError("Missing 'lokasi' or 'data' key in response")

    try:
        return BMKGForecast.model_validate(json_data)
    except Exception as exc:
        raise BMKGParseError(f"Validation failed: {exc}") from exc

def get_sample_villages() -> List[VillageIndex]:
    """
    Return sample villages for demo purposes.
    One representative village per province.

    Kode ADM4 sources:
    - Keputusan Menteri Dalam Negeri nomor 100.1.1-6117 Tahun 2022
    - Github https://github.com/infoBMKG/data-cuaca
    """
    villages = [
        # ("adm4", "adm1", "Provinsi", "adm2", "Kota/Kab", "adm3", "Kecamatan", "Desa")
        ("11.01.01.1001", "11", "Aceh", "11.01", "Kabupaten Simeulue", "11.01.01", "Teupah Selatan", "Teupah Selatan"),
        ("12.01.02.1001", "12", "Sumatera Utara", "12.01", "Kabupaten Tapanuli Tengah", "12.01.02", "Pandan", "Pandan"),
        ("31.71.03.1001", "31", "DKI Jakarta", "31.71", "Kota Adm. Jakarta Pusat", "31.71.03", "Kemayoran", "Kemayoran"),
        ("32.01.01.1001", "32", "Jawa Barat", "32.01", "Kabupaten Bogor", "32.01.01", "Cibinong", "Cibinong"),
        # Add remaining provinces...
    ]

    base_url = "https://api.bmkg.go.id"
    return [
        VillageIndex.from_adm4(
            adm4=v[0], adm1=v[1], provinsi=v[2],
            adm2=v[3], kotkab=v[4], adm3=v[5],
            kecamatan=v[6], adm4_short=v[7],
            base_url=base_url
        )
        for v in villages
    ]

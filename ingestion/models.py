"""
Pydantic models for BMKG weather data (JSON API).

API: https://api.bmkg.go.id/publik/prakiraan-cuaca?amd4={kode_desa}.
format: JSON
"""

from datetime import datetime as DateTime 
from typing import List, Optional

from pydantic import BaseModel, Field

class Location(BaseModel):
    """ Location metadata from BMKG response. """
    adm1: Optional[str] = Field(default=None, description="Province code")
    adm2: Optional[str] = Field(default=None, description="City/kabupaten code")
    adm3: Optional[str] = Field(default=None, description="Kecamatan code")
    adm4: Optional[str] = Field(default=None, description="Desa/kelurahan code (adm4)")
    provinsi: Optional[str] = Field(default=None, alias="provinsi")
    kotkab: Optional[str] = Field(default=None)
    kecamatan: Optional[str] = Field(default=None)
    desa: Optional[str] = Field(default=None)
    lon: Optional[float] = Field(default=None)
    lat: Optional[float] = Field(default=None)
    timezone: Optional[str] = Field(default=None)

    model_config = {"populate_by_name": True}

class WeatherEntry(BaseModel):
    """ Single weather observation (3-hourly). """
    datetime: Optional[DateTime] = Field(default=None)
    utc_datetime: Optional[str] = Field(default=None)
    local_datetime: Optional[str] = Field(default=None)
    t: Optional[float] = Field(default=None, description="Suhu °C")
    tcc: Optional[float] = Field(default=None, description="Tutupan awan %")
    tp: Optional[float] = Field(default=None, description="Presipitasi mm")
    weather: Optional[int] = Field(default=None, description="Kode cuaca")
    weather_desc: Optional[str] = Field(default=None, description="Deskripsi ID")
    weather_desc_en: Optional[str] = Field(default=None, description="Deskripsi EN")
    wd_deg: Optional[float] = Field(default=None, description="Arah angin °")
    wd: Optional[str] = Field(default=None, description="Arah angin N/S/E/W")
    wd_to: Optional[str] = Field(default=None, description="Angin ke arah")
    ws: Optional[float] = Field(default=None, description="Kecepatan angin km/jam")
    hu: Optional[int] = Field(default=None, description="Kelembapan %")
    vs: Optional[int] = Field(default=None, description="Visibilitas meter")
    vs_text: Optional[str] = Field(default=None, description="Visibilitas text")
    time_index: Optional[str] = Field(default=None)
    analysis_date: Optional[str] = Field(default=None)

class DataBlock(BaseModel):
    """ Single data block with location +  (3 days). """
    lokasi: Optional["Location"] = Field(default=None)
    cuaca: Optional[List[List[WeatherEntry]]] = Field(default_factory=list)

class BMKGForecast(BaseModel):
    """ Root model for BMKG API JSON Response. """
    lokasi: Optional["Location"] = Field(default=None)
    data: Optional[List[DataBlock]] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True
    }

class VillageIndex(BaseModel):
    """ 
    Index entry - links ADM4 village code to province info.
    Kode ADM4: 4-level administrative code (Kepmenagri No.100.1.1-6117/2022)
    Example: 31.71.03.1001 = DKI Jakarta, Jakarta Pusat, Kemayoran, Kemayoran
    """

    adm4: str = Field(description="ADM4 village code")
    adm1: str = Field(description="Province code")
    provinsi: str = Field(description="Province name")
    adm2: str = Field(description="City/kabupaten code")
    kotkab: str = Field(description="City/kabupaten name")
    adm3: str = Field(description="Kecamatan code")
    kecamatan: str = Field(description="Kecamatan name")
    adm4_short: str = Field(description="Village name (from ADM4)")
    api_url: str = Field(description="FULL API URL")

    @classmethod
    def from_adm4(
        cls,
        adm4: str,
        adm1: str,
        provinsi: str,
        adm2: str,
        kotkab: str,
        adm3: str,
        kecamatan: str,
        adm4_short: str,
        base_url: str = "https://api.bmkg.go.id"
    ) -> "VillageIndex":
        return cls(
            adm4=adm4,
            adm1=adm1,
            provinsi=provinsi,
            adm2=adm2,
            kotkab=kotkab,
            adm3=adm3,
            kecamatan=kecamatan,
            adm4_short=adm4_short,
            api_url=f"{base_url}/publik/prakiraan-cuaca?adm4={adm4}"
        )
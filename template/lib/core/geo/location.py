import logging
import geoip2.database
from typing import Dict, Optional

def get_location_info(ip_address: str) -> Dict[str, str]:
    """
    Get location information from IP address.
    
    Args:
        ip_address (str): The IP address to look up
        
    Returns:
        Dict[str, str]: Dictionary containing location information or empty dict if lookup fails
    """
    if not ip_address or ip_address == "127.0.0.1":
        return {}
    
    try:
        # Using the GeoLite2 database from GitHub: https://github.com/P3TERX/GeoLite.mmdb
        reader = geoip2.database.Reader('lib/core/geo/GeoLite2-City.mmdb')
        response = reader.city(ip_address)
        
        return {
            "country": response.country.name,
            "country_code": response.country.iso_code,
            "city": response.city.name,
            "latitude": str(response.location.latitude),
            "longitude": str(response.location.longitude),
            "timezone": response.location.time_zone
        }
    except Exception as e:
        return {}
    finally:
        if 'reader' in locals():
            reader.close()

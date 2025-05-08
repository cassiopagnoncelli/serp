from typing import Dict
from user_agents import parse

def get_device_info(user_agent: str) -> Dict:
    """
    Extract detailed device information from user agent string.
    
    Args:
        user_agent (str): The user agent string to parse
        
    Returns:
        Dict: Dictionary containing device information or empty dict if parsing fails
    """
    if not user_agent:
        return {}
    
    try:
        ua = parse(user_agent)
        return {
            "browser": {
                "family": ua.browser.family,
                "version": ua.browser.version_string,
            },
            "os": {
                "family": ua.os.family,
                "version": ua.os.version_string,
            },
            "device": {
                "family": ua.device.family,
                "brand": ua.device.brand,
                "model": ua.device.model,
                "is_mobile": ua.is_mobile,
                "is_tablet": ua.is_tablet,
                "is_pc": ua.is_pc,
            }
        }
    except Exception as e:
        return {} 
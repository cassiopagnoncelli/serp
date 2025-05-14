from datetime import datetime, date
import xml.etree.ElementTree as ET
from typing import Any, Dict

def _dict_to_xml(data: Dict[str, Any], root_name: str = "root") -> str:
    """Convert a dictionary to XML string."""
    def _create_element(parent: ET.Element, key: str, value: Any) -> None:
        if isinstance(value, dict):
            child = ET.SubElement(parent, key)
            for k, v in value.items():
                _create_element(child, k, v)
        elif isinstance(value, list):
            for item in value:
                child = ET.SubElement(parent, key)
                if isinstance(item, dict):
                    for k, v in item.items():
                        _create_element(child, k, v)
                else:
                    child.text = str(item)
        else:
            child = ET.SubElement(parent, key)
            if isinstance(value, (datetime, date)):
                child.text = value.isoformat()
            else:
                child.text = str(value)

    root = ET.Element(root_name)
    for key, value in data.items():
        _create_element(root, key, value)
    
    return ET.tostring(root, encoding='unicode')

def serialize_xml(obj: Dict[str, Any]) -> str:
    """Serialize a dictionary to XML string."""
    return _dict_to_xml(obj)

def _parse_element(element: ET.Element) -> Any:
    """Parse an XML element into a Python object."""
    if len(element) > 0:
        if all(child.tag == element[0].tag for child in element):
            # If all children have the same tag, treat as a list
            return [_parse_element(child) for child in element]
        else:
            # Otherwise treat as a dictionary
            return {child.tag: _parse_element(child) for child in element}
    return element.text

def deserialize_xml(xml_str: str) -> Dict[str, Any]:
    """Deserialize an XML string to a dictionary."""
    root = ET.fromstring(xml_str)
    return {root.tag: _parse_element(root)} 
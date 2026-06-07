#!/usr/bin/env python3
"""
NFO Parser
Parses NFO metadata files.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Optional
from loguru import logger


class NFOParser:
    """Parses NFO metadata files"""

    def parse(self, nfo_path: str) -> Dict:
        """
        Parse NFO file
        
        Args:
            nfo_path: Path to NFO file
            
        Returns:
            Dictionary of parsed metadata
        """
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            
            data = {}
            for child in root:
                data[child.tag] = child.text
            
            logger.debug(f"Parsed NFO: {nfo_path}")
            return data
            
        except Exception as e:
            logger.warning(f"Error parsing NFO {nfo_path}: {e}")
            return {}

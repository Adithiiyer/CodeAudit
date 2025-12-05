"""
Perfect code example with good practices.
This module demonstrates clean, well-documented code.
"""

import logging
from typing import List, Dict, Any


class DataProcessor:
    """
    A class for processing data with proper documentation.
    
    Attributes:
        data: The data to process
        logger: Logger instance for tracking operations
    """
    
    def __init__(self, data: List[Any]):
        """Initialize the processor with data."""
        self.data = data
        self.logger = logging.getLogger(__name__)
    
    def process(self) -> Dict[str, Any]:
        """
        Process the data and return results.
        
        Returns:
            Dictionary containing processed results
        """
        self.logger.info("Processing started")
        results = {"count": len(self.data), "status": "complete"}
        self.logger.info("Processing finished")
        return results
    
    def validate(self) -> bool:
        """
        Validate the data.
        
        Returns:
            True if valid, False otherwise
        """
        return isinstance(self.data, list)


def main():
    """Main function to demonstrate usage."""
    processor = DataProcessor([1, 2, 3, 4, 5])
    results = processor.process()
    print(f"Results: {results}")


if __name__ == "__main__":
    main()
# Well-structured file with good error handling
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    """Process and validate data."""
    try:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        return data
    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        return None
    except Exception as e:
        logger.exception("Unexpected error occurred")
        return None

def main():
    """Main entry point."""
    data = {"key": "value"}
    result = process_data(data)
    return result

if __name__ == "__main__":
    main()

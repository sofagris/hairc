# Release Notes

## Version 0.1.2 (2024-01-03)

### Stability Improvements
- Added comprehensive error handling
- Implemented automatic reconnection with exponential backoff
- Limited message storage to prevent memory issues
- Added proper cleanup on shutdown
- Improved connection state management

### Known Issues
- Compatibility issue with Python 3.13:
  - Error: `ImportError: cannot import name 'coroutine' from 'asyncio'`
  - Cause: The `coroutine` decorator was removed from `asyncio` in Python 3.13
  - Workaround: Use Python 3.12 or earlier until pydle library is updated
  - Status: Investigating alternative solutions

### New Features
- Initial release of the IRC Home Assistant Integration
- Support for connecting to IRC servers and channels
- SSL encryption support
- Server password support
- Incoming message logging
- GUI configuration interface

### Installation Methods
- Added HACS installation support
- Maintained manual installation option

### Documentation
- Added comprehensive documentation in multiple languages:
  - English (default)
  - Nordic languages:
    - Norwegian
    - Swedish
    - Danish
    - Finnish
  - Major languages:
    - Spanish
    - French
    - German
    - Chinese (Simplified)
    - Japanese
- Updated installation instructions for HACS
- Added troubleshooting guide
- Added contribution guidelines

### Technical Details
- Compatible with Home Assistant 2024.1.0 and later
- Supports sensor and binary_sensor domains
- Local push IoT class
- Persistent directory support for user files
- Maximum of 100 stored messages
- Automatic reconnection with 5-minute maximum retry interval

### Dependencies
- pydle>=0.9.4 (requires Python 3.12 or earlier)
- Home Assistant Core 2024.1.0 or later
- HACS (optional, for easy installation) 
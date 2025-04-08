# Release Notes

## Version 0.1.3 (2025-04-08)

### Breaking Changes
- Switched from pydle to Twisted as IRC library
  - Reason: Better support for newer Python versions and more mature library
  - Impact: Existing configurations will still work, but requires Home Assistant restart
  - Migration: No migration needed, but recommended to remove and re-add the integration

### New Features
- Improved error handling and reconnection logic
- Added support for both private and public messages
- Added a maximum limit for stored messages (100 messages)

### Technical Details
- Using Twisted>=22.10.0 as IRC library
- Full support for Python 3.13
- Improved connection and message handling
- More robust error handling

### Dependencies
- Twisted>=22.10.0

## Version 0.1.2 (2025-04-08)

### Changed
- Updated documentation link to correct repository
- Updated codeowners to correct username

## Version 0.1.1 (2025-04-08) - Withdrawn

### Critical Issues
- Version was withdrawn due to Home Assistant crash
- Issues with irc3 library and Python 3.13

## Version 0.1.0 (2025-04-08)

### New Features
- Initial release of IRC Home Assistant Integration
- Support for connecting to IRC servers
- Support for SSL encryption
- Support for server passwords
- Support for incoming messages
- GUI configuration

### Technical Details
- Using pydle>=0.9.4 as IRC library
- Supports both private and public messages
- Shows connection status in Home Assistant
- Stores the last 10 messages

### Dependencies
- pydle>=0.9.4

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
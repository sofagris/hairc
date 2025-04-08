# Release Notes

## Version 0.1.0 (2024-01-01)

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

### Known Issues
- Compatibility issue with Python 3.13:
  - Error: `ImportError: cannot import name 'coroutine' from 'asyncio'`
  - Cause: The `coroutine` decorator was removed from `asyncio` in Python 3.13
  - Workaround: Use Python 3.12 or earlier until pydle library is updated
  - Status: Waiting for pydle library update

### Alternative IRC Libraries
- irc3: Modern IRC library with asyncio support
  - Pros: Actively maintained, Python 3.13 compatible
  - Cons: Less mature than pydle
- irc: Well-established IRC library
  - Pros: Stable, widely used
  - Cons: No native asyncio support
- irclib: Lightweight IRC library
  - Pros: Simple to use, minimal dependencies
  - Cons: Limited features
- aiirc: Async IRC library
  - Pros: Modern, async-first design
  - Cons: Less documentation

### Breaking Changes
- None in initial release

### Dependencies
- pydle IRC library (requires Python 3.12 or earlier)
- Home Assistant Core 2024.1.0 or later
- HACS (optional, for easy installation) 
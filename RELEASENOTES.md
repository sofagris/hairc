# Release Notes

## Version 0.1.1 (2024-01-02)

### Breaking Changes
- Switched from pydle to irc3 library
  - Reason: Python 3.13 compatibility issues with pydle
  - Impact: Requires reinstallation of the integration
  - Migration: Remove old integration and install new version

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
- Uses irc3 library for IRC communication
  - Better Python 3.13 compatibility
  - Improved message handling
  - Enhanced connection management

### Known Issues
- None reported in current release

### Dependencies
- irc3>=0.12.0
- Home Assistant Core 2024.1.0 or later
- HACS (optional, for easy installation) 
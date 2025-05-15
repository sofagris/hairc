# Changelog

## [1.1.0] - 2025-05-15
### Added
- Structured message format with timestamp
- Separate fields for nick and host in messages
- Improved message display in Home Assistant

## [1.0.0] - 2025-05-15
### Added
- Initial release
- Basic IRC integration
- Support for SSL connections
- Auto-reconnect functionality
- Message handling
- Service for sending messages

## [0.1.5] - 2025-04-08

### Fixed
- Fixed shutdown error when transport is None
- Improved connection state management
- Added proper transport handling in IRC client
- Added service_identity dependency for proper SSL/TLS support

## [0.1.4] - 2025-04-08

### Changed
- Switched from pydle to Twisted as IRC library
- Improved error handling and reconnection logic
- Added support for both private and public messages
- Added a maximum limit for stored messages

## [0.1.3] - 2025-04-08

### Changed
- Updated documentation link to correct repository
- Updated codeowners to correct username

## [0.1.2] - 2025-04-08 (Withdrawn)

### Changed
- Switched from pydle to irc3 as IRC library
- Improved error handling and reconnection logic
- Added support for both private and public messages
- Added a maximum limit for stored messages

### Critical Issues
- Version was withdrawn due to Home Assistant crash

## [0.1.1] - 2025-04-08

### Added
- Initial release of IRC Home Assistant Integration
- Support for connecting to IRC servers
- Support for SSL encryption
- Support for server passwords
- Support for incoming messages
- GUI configuration
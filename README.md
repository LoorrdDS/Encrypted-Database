# CLASSIFIED DATABASE

A secure console-based intelligence database system inspired by real-world intelligence agencies.

## Features

* User authentication system
* Multiple user roles and clearance levels
* Encrypted database storage using Fernet encryption
* Secure user management
* Creation, editing and deletion of classified records
* Clearance-based access control
* Search functionality
* Redacted information for unauthorized users
* Multi-line intelligence reports using EOF termination
* Automatic encrypted storage of all records
* Console-based interface

## User Roles

| Role          | Clearance  |
| ------------- | ---------- |
| Viewer        | PUBLIC     |
| Informant     | PUBLIC     |
| Agent         | INTERN     |
| Officer       | GEHEIM     |
| Director      | TOP_SECRET |
| Administrator | TOP_SECRET |

## Security

All database and user information is stored in encrypted files using AES-based Fernet encryption.

Required files:

* geheimdatenbank.enc
* users.enc
* salt.bin

Without the correct encryption key and salt file, stored information cannot be decrypted.

## Usage

### Login

Start the application and authenticate using your assigned credentials.

### Creating Records

When entering intelligence reports, normal ENTER creates a new line.

To save the report, enter:

EOF

on a separate line.

Example:

Agent observed in Berlin.

Contact established with local asset.

Surveillance continues.

EOF

### Search

Use the integrated search engine to locate records based on:

* Codename
* Category
* Content
* Status
* Record ID

## Disclaimer

This software is intended for educational, hobby and entertainment purposes only.

It is not affiliated with, endorsed by or connected to any government agency, intelligence service or military organization.

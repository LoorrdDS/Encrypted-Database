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

## Initial Setup

Upon first launch, you will be prompted to create a **Master Key**. This key is used to encrypt and decrypt all database files.

**Important:**
If you lose your Master Key, your data cannot be recovered. There is no backdoor, recovery mechanism, or password reset functionality.

### Default Administrator Account

For the initial setup, log in using the default administrator credentials:

**Username:** admin
**Password:** admin123

### User Management

After logging in as Administrator, you can create additional user accounts and assign different roles and clearance levels according to your operational requirements.

It is strongly recommended to change the default administrator password immediately after the first login.


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

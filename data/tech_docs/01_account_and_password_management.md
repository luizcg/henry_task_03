# Account and Password Management Guide - Acme Corporation IT

## Overview

This document explains how Acme employees manage their corporate accounts and passwords, including account creation, password reset, MFA (multi-factor authentication), and account lockouts.

## Account Types

Acme provides several types of accounts:

- **Network account (AcmeID)** – Used to sign in to your laptop, VPN, and internal systems.
- **Email account (Office 365)** – Corporate email, calendar, and contacts.
- **Single Sign-On (SSO) account** – Used to access most SaaS applications (Jira, Confluence, Salesforce, etc.).
- **Admin accounts** – Elevated privilege accounts for IT and engineering (granted only when necessary).

Most employees have one primary AcmeID that is synchronized across systems.

## Initial Account Setup

### Before Your First Day

1. You will receive a **"Welcome to Acme IT"** email at your personal address.
2. The email contains:
   - Your temporary AcmeID username
   - Instructions for setting your initial password
   - Link to enroll in MFA

### First Login

1. Go to **https://account.acme-corp.com/first-login**.
2. Enter your AcmeID and temporary password.
3. You will be prompted to:
   - Create a new password
   - Set up MFA (authenticator app or SMS)
   - Set security questions (used as backup verification)

## Password Requirements

Your Acme password must meet these requirements:

- Minimum 12 characters
- At least 1 uppercase letter (A–Z)
- At least 1 lowercase letter (a–z)
- At least 1 number (0–9)
- At least 1 special character (!@#$%^&* or similar)
- Cannot contain your first name, last name, or username
- Cannot be identical to any of your last 10 passwords

Passwords expire every **180 days**. You will receive reminder emails 14, 7, and 3 days before expiration.

## Password Reset (Self-Service)

If you forget your password but still have access to your phone or MFA device, use the self-service portal.

### Steps to Reset Your Password

1. Go to **https://account.acme-corp.com/reset**.
2. Enter your AcmeID or corporate email address.
3. Choose a verification method:
   - Authenticator app code
   - SMS code
   - Backup email (if configured)
4. Enter the code received.
5. Set a new password following the requirements listed above.

If successful, your new password will work for:
- Laptop login (next sign-in)
- VPN
- SSO and internal apps (may take up to 5 minutes to sync)

## Password Reset (Help Desk Assisted)

If you:
- Lost your phone or no longer have access to MFA
- Forgot your password and cannot access the self-service portal
- Believe your account may be compromised

Contact the **IT Help Desk**:

- Email: it-help@acme-corp.com
- Phone: +1 (800) 555-4357 (HELP)
- Slack: #it-help

Be prepared to verify your identity by:
- Providing your employee ID
- Answering security questions
- Confirming recent login activity

IT will never ask you for your full password.

## Multi-Factor Authentication (MFA)

### Why MFA Is Required

MFA greatly reduces the risk of account compromise. All remote access and most internal applications require MFA.

### Supported MFA Methods

- Authenticator app (recommended): Microsoft Authenticator, Google Authenticator, Authy
- SMS-based codes (backup method)
- Hardware token (for specific roles or where phones are not allowed)

### Enrolling in MFA

1. Install an authenticator app on your phone.
2. Visit **https://account.acme-corp.com/mfa-setup**.
3. Sign in with your AcmeID and password.
4. Scan the QR code with your authenticator app.
5. Enter the 6-digit code from the app to verify.
6. Add a backup method (SMS or backup codes).

### Lost or Replaced Phone

If you change or lose your phone:
- If you still have the old device, transfer your MFA app to the new device.
- If you cannot access MFA at all, contact the IT Help Desk to reset your MFA.

## Account Lockouts

### Automatic Lockouts

Your account may be automatically locked if:
- You enter the wrong password 10 times in a row.
- Suspicious login activity is detected (e.g., impossible travel, unusual IP).

### What to Do if Locked Out

1. Wait 15 minutes; in many cases, the account will unlock automatically.
2. Use the **self-service password reset** portal if you suspect you forgot your password.
3. If you continue to have issues, contact IT Help Desk.

### Security Holds

In some cases, Security may place a hold on your account:
- Suspected compromise
- Termination or leave of absence
- Policy violations under investigation

If this occurs, you will be notified via personal email or HR.

## Shared and Service Accounts

### Shared Mailboxes

Some teams use shared mailboxes (e.g., support@acme-corp.com):
- Access is granted through group membership.
- Do not share your personal password with colleagues to access shared mailboxes.

### Service Accounts

Service accounts are used by applications and automated processes:
- Managed by IT or Engineering only.
- Must use long, randomly generated passwords and/or key-based auth.
- Should not be used for interactive logins unless explicitly approved.

## Security Best Practices

- Never share your password with anyone, including IT.
- Do not reuse your Acme password on other sites.
- Be cautious of phishing emails and suspicious links.
- Approve MFA prompts only when you are actively logging in.
- Report unexpected MFA prompts to Security immediately.

## Frequently Asked Questions

**Q: I know my password is correct, but it still fails. What should I do?**
A: Your account may be locked out or out of sync. Wait 15 minutes, then try again. If it still fails, use the reset portal or contact IT.

**Q: How do I change my password before it expires?**
A: Go to **https://account.acme-corp.com/change-password** while logged in.

**Q: I received an MFA prompt I did not initiate. What now?**
A: Deny the request and contact Security at security@acme-corp.com and IT Help Desk immediately.

**Q: Can I use a password manager?**
A: Yes, Acme recommends using the approved corporate password manager (see Security Policy) for work-related credentials.

## Contacts

- IT Help Desk: it-help@acme-corp.com
- Security Team: security@acme-corp.com
- Account Portal: https://account.acme-corp.com

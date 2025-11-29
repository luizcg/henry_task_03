# Mobile Device Management (MDM) Policy

## Overview

Acme Corporation uses Mobile Device Management (MDM) to secure corporate data on mobile devices. This policy applies to both company-issued and personal devices (BYOD) that access corporate resources.

## Supported Devices

### Company-Issued Devices
- iPhone 12 or newer (iOS 15+)
- Samsung Galaxy S21 or newer (Android 12+)
- iPad Pro (current and previous generation)

### BYOD (Bring Your Own Device)
Personal devices may access corporate email and apps if they meet minimum requirements:
- iOS 15 or later
- Android 12 or later
- Device encryption enabled
- Screen lock configured

## MDM Enrollment

### Company-Issued Devices
Company devices are pre-enrolled before distribution. Simply sign in with your corporate credentials during initial setup.

### Personal Devices (BYOD)

To enroll your personal device:

1. **Download Microsoft Intune Company Portal**
   - iOS: App Store
   - Android: Google Play Store

2. **Sign In**
   - Use your corporate email and password
   - Complete MFA verification

3. **Accept Policies**
   - Review the privacy statement
   - Accept the terms of use
   - Grant required permissions

4. **Complete Setup**
   - Allow profile installation (iOS)
   - Enable device administrator (Android)
   - Wait for compliance check

## What MDM Can and Cannot Do

### What IT CAN See
- Device type, model, and OS version
- Corporate apps installed
- Compliance status
- Device encryption status

### What IT CANNOT See
- Personal photos and videos
- Personal text messages
- Personal app data
- Browsing history
- Location (unless lost device mode)

### What IT CAN Do
- Push corporate apps
- Enforce security policies
- Remote wipe corporate data only (BYOD)
- Full remote wipe (company devices only)

## Security Requirements

### All Enrolled Devices Must Have

1. **Screen Lock**
   - Minimum 6-digit PIN or biometric
   - Auto-lock after 5 minutes of inactivity

2. **Device Encryption**
   - Full disk encryption enabled
   - Automatic on modern iOS/Android

3. **OS Updates**
   - Install security updates within 7 days
   - Major OS updates within 30 days

4. **No Jailbreak/Root**
   - Jailbroken or rooted devices are blocked
   - Compliance checked daily

## Corporate Apps

### Required Apps (Auto-Installed)
- Microsoft Outlook
- Microsoft Teams
- Microsoft Authenticator
- Intune Company Portal

### Optional Apps (Available in Company Portal)
- OneDrive for Business
- SharePoint
- Power BI
- Adobe Acrobat Reader

### App Protection Policies

Corporate apps have additional protections:
- Copy/paste between corporate and personal apps: Blocked
- Screenshots of corporate apps: Allowed (but logged)
- Save to personal cloud: Blocked
- Open in personal apps: Blocked

## Lost or Stolen Devices

### Immediate Steps
1. Report to IT immediately: Extension 4357 or it-support@acmecorp.com
2. IT will initiate remote locate (if enabled)
3. Remote wipe will be performed if device cannot be recovered

### Company Devices
- Full remote wipe (returns device to factory settings)
- Report to security if sensitive data was accessed

### Personal Devices (BYOD)
- Selective wipe (removes only corporate data and apps)
- Personal data remains intact

## Offboarding

### When Leaving the Company
- Company devices must be returned to IT
- BYOD devices will receive selective wipe
- Remove MDM profile after corporate data is wiped

### Voluntary Unenrollment (BYOD)
You may remove MDM at any time:
1. Open Intune Company Portal
2. Go to Devices
3. Select your device
4. Tap "Remove"

Note: Removing MDM will also remove access to corporate email and apps.

## Troubleshooting

### Device Shows Non-Compliant
1. Check which policy is violated in Company Portal
2. Common issues:
   - OS update required
   - Screen lock not configured
   - Encryption not enabled
3. Fix the issue and wait for compliance recheck (up to 8 hours)

### Cannot Install Corporate Apps
1. Verify device is enrolled and compliant
2. Check available storage space
3. Try installing from Company Portal app
4. Restart device and retry

### MDM Profile Installation Failed (iOS)
1. Go to Settings > General > VPN & Device Management
2. Remove any existing MDM profiles
3. Retry enrollment from Company Portal

## Support

- **IT Service Portal**: https://ithelp.acmecorp.com
- **Email**: it-support@acmecorp.com
- **Phone**: Extension 4357 (HELP)
- **Emergency (lost/stolen)**: security@acmecorp.com

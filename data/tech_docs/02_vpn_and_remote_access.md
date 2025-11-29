# VPN and Remote Access Guide - Acme Corporation IT

## Overview

This document explains how to connect securely to Acme's internal network from outside the office using VPN (Virtual Private Network) and other remote access tools.

## When You Need VPN

You need VPN access when you:

- Work remotely (home, coworking space, hotel, etc.) and need to access internal resources.
- Connect to systems that are only available on the corporate network, such as:
  - Internal dashboards
  - Staging/production environments (for authorized users)
  - File servers and on-prem databases

You generally **do not** need VPN for:

- Email (Office 365)
- Slack
- Most SaaS tools (Jira, Confluence, Salesforce, etc.)

## VPN Requirements

To use VPN, you must have:

- A company-managed laptop (Windows or macOS)
- A valid AcmeID and password
- MFA (multi-factor authentication) set up
- The Acme VPN client installed (GlobalSecure VPN)

If any of these are missing, contact IT Help Desk.

## Installing the VPN Client

### Windows

1. Open the **Company Portal** app.
2. Search for **GlobalSecure VPN**.
3. Click **Install**.
4. After installation, you will see the VPN client in the Start menu.

### macOS

1. Open **Self Service** (Acme's app catalog for Mac).
2. Locate **GlobalSecure VPN**.
3. Click **Install**.
4. The VPN client will appear in your Applications folder and menu bar.

If you do not see the VPN client in the portal/catalog, contact IT.

## Connecting to VPN

1. Open the **GlobalSecure VPN** client.
2. Choose the nearest gateway (e.g., "US-West", "US-East", "EU-Central").
3. Click **Connect**.
4. When prompted, enter your AcmeID and password.
5. Complete the MFA challenge on your phone.
6. Wait for the status to show **Connected**.

You should now be able to access internal resources.

## Disconnecting from VPN

- Click **Disconnect** in the VPN client when you no longer need secure access.
- Disconnect at the end of your workday to reduce load on the network.

## Troubleshooting VPN Issues

### Common Problems and Solutions

**Problem: VPN client will not connect ("Connection Failed").**
- Check your internet connection.
- Try switching to a different Wi-Fi network or tethering.
- Choose a different VPN gateway (e.g., switch from US-West to US-East).
- Restart your laptop and try again.

**Problem: MFA prompt not received.**
- Confirm that your phone has an internet connection.
- Open your authenticator app to see if a code is available.
- If using SMS, check for signal and retry.
- If you recently changed phones, your MFA may need to be re-enrolled (contact IT).

**Problem: Connected to VPN but cannot reach internal sites.**
- Try disconnecting and reconnecting VPN.
- Verify that DNS is working by accessing an internal hostname.
- If still an issue, capture a screenshot and contact IT.

**Problem: VPN disconnects frequently.**
- Check your local network stability.
- Avoid public Wi-Fi if possible; use wired or secure home Wi-Fi.
- Close bandwidth-intensive apps (video streaming, large downloads).

## Remote Desktop Access

Some employees need access to on-site desktops or lab machines.

### Requesting Remote Desktop Access

1. Submit a ticket via **it.acme-corp.com** with the subject "Remote Desktop Access".
2. Include:
   - The hostname or asset tag of the target machine
   - Your use case (why you need remote desktop)
   - Your manager in CC for approval

3. IT will review and configure access via Remote Desktop Gateway or similar tools.

### Using Remote Desktop

- Connect to VPN first.
- Launch the Remote Desktop client (Windows or Microsoft Remote Desktop on Mac).
- Enter the hostname provided by IT.
- Log in with your network credentials.

## Security Guidelines for Remote Access

- Use only company-managed devices for VPN and remote desktop.
- Do not share your VPN or Remote Desktop credentials.
- Lock your laptop when away, even at home.
- Avoid using public or shared computers to access corporate resources.

## Working from Public Networks

When using hotel, café, or airport Wi-Fi:

- Always connect to VPN before accessing internal resources.
- Avoid sensitive transactions (e.g., accessing production systems) if the connection is unstable.
- Be aware of your surroundings; do not display sensitive information where it can be seen.

## Frequently Asked Questions

**Q: Do I need VPN to check my email from home?**
A: No. Email is hosted in the cloud and available without VPN.

**Q: My VPN client says "No licenses available". What should I do?**
A: This means the VPN service is at capacity. Wait a few minutes and try again. If the issue persists, contact IT.

**Q: Can I install the VPN client on my personal computer?**
A: No. VPN is only supported on company-managed devices for security reasons.

**Q: Can I stay connected to VPN all the time?**
A: You can, but we recommend disconnecting when you do not need access to internal resources to reduce network load.

## Contacts

- IT Help Desk: it-help@acme-corp.com
- VPN Support: vpn-support@acme-corp.com
- Security Team: security@acme-corp.com

# Printing and Scanning Guide

## Overview

Acme Corporation provides networked multifunction printers (MFPs) throughout all office locations. This guide covers how to set up printing, use scanning features, and troubleshoot common issues.

## Printer Locations

### Headquarters
- **Floor 1**: Copy room near reception (Color MFP)
- **Floor 2**: North wing break room (B&W MFP), South wing near elevators (Color MFP)
- **Floor 3**: Central copy room (2x Color MFP, 1x B&W high-volume)
- **Floor 4**: Executive wing (Color MFP with secure print)

### Branch Offices
Each branch has at least one color MFP in the main work area. Check with your local office manager for specific locations.

## Print Setup

### Windows (Company Laptops)
Printers are automatically installed via group policy. To verify:
1. Open Settings > Printers & Scanners
2. Look for printers named "ACME-[Location]-[Type]"
3. If missing, restart your laptop while connected to corporate network

### Mac (Company Laptops)
1. Open System Preferences > Printers & Scanners
2. Click the + button
3. Select the printer from the list (auto-discovered)
4. Click Add

### Manual Installation
If automatic installation fails:
1. Open the IT Service Portal
2. Search for "Printer Drivers"
3. Download the driver package for your OS
4. Follow installation instructions

## Secure Print (Follow-Me Printing)

All Acme printers support Secure Print, which holds your job until you authenticate at the printer.

### How to Use Secure Print

1. **Print from your computer**
   - Select the Secure Print queue (e.g., "ACME-SecurePrint")
   - Enter a 4-digit PIN when prompted

2. **Release at any printer**
   - Walk to any Secure Print enabled MFP
   - Tap your badge or enter your employee ID
   - Enter your PIN
   - Select jobs to print or print all

### Benefits
- Documents don't sit unclaimed in the tray
- Print from anywhere, release at nearest printer
- Confidential documents stay secure

### Secure Print Jobs Expire
- Jobs are held for 24 hours
- Unreleased jobs are automatically deleted
- No charges for unclaimed secure print jobs

## Scanning

### Scan to Email
1. Place document in feeder or on glass
2. Tap "Scan to Email" on the touchscreen
3. Tap your badge or enter credentials
4. Your email is pre-filled as the recipient
5. Add additional recipients if needed
6. Select format (PDF recommended) and press Start

### Scan to OneDrive
1. Place document in feeder or on glass
2. Tap "Scan to Cloud"
3. Authenticate with your badge
4. Select OneDrive as destination
5. Choose folder location
6. Press Start

### Scan Settings

| Setting | Options | Recommended |
|---------|---------|-------------|
| Color | Color, Grayscale, B&W | Grayscale for text documents |
| Resolution | 150, 300, 600 DPI | 300 DPI for most uses |
| Format | PDF, JPEG, TIFF | PDF for documents |
| Double-sided | On/Off | On for multi-page documents |

## Copying

### Basic Copying
1. Place original on glass or in document feeder
2. Tap "Copy" on touchscreen
3. Select number of copies
4. Adjust settings if needed
5. Press Start

### Advanced Copy Features
- **Duplex**: Print on both sides
- **N-up**: Multiple pages per sheet (2-up, 4-up)
- **Collate**: Keep multi-page documents in order
- **Staple**: Available on select MFPs
- **Hole punch**: Available on select MFPs

## Print Policies

### Color Printing
- Color printing is tracked by department
- Use black & white for internal documents
- Color approved for client-facing materials

### Paper Usage
- Default: Double-sided printing
- Use single-sided only when necessary
- Draft mode for internal reviews

### Large Print Jobs
- Jobs over 100 pages: Use B&W high-volume printer
- Jobs over 500 pages: Submit to print shop (printshop@acmecorp.com)

## Cost Allocation

Printing costs are allocated to departments:
- **B&W**: $0.02 per page
- **Color**: $0.10 per page
- Monthly reports sent to department managers

Personal printing is not permitted on corporate printers.

## Troubleshooting

### Paper Jam
1. Open indicated doors (shown on display)
2. Gently remove jammed paper
3. Close all doors
4. Press Continue on display

### Print Job Not Appearing
1. Verify correct printer selected
2. Check if job is in Secure Print queue
3. Restart print spooler (Windows: services.msc > Print Spooler > Restart)
4. Try printing a test page

### Poor Print Quality
1. Run cleaning cycle from printer menu
2. Check toner/ink levels
3. Verify correct paper type settings
4. Report persistent issues to IT

### Scan Not Received
1. Check spam/junk folder
2. Verify email address was entered correctly
3. Check OneDrive if scanning to cloud
4. Try scanning again with confirmation enabled

### Cannot Authenticate at Printer
1. Ensure badge is enrolled (IT can verify)
2. Try manual entry with employee ID and PIN
3. Contact IT if authentication consistently fails

## Supplies

### Requesting Supplies
- Paper: Contact office admin or facilities
- Toner: Automatically ordered when low
- Specialty paper: Request through IT Service Portal

### Loading Paper
1. Pull out paper tray
2. Adjust guides to paper size
3. Load paper (print side up for most trays)
4. Push tray in until it clicks
5. Confirm paper type on display if prompted

## Support

- **IT Service Portal**: https://ithelp.acmecorp.com
- **Printer Issues**: Submit ticket under "Printing"
- **Urgent Issues**: Extension 4357 (HELP)
- **Print Shop**: printshop@acmecorp.com

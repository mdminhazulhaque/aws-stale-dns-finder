# AWS Stale DNS Finder

![AWS Stale DNS Finder](.media/aws-stale-dns-finder.drawio.png)

## Overview

AWS Stale DNS Finder is a comprehensive tool that identifies orphaned and stale DNS records across your AWS infrastructure. It cross-references Route 53 DNS records with actual AWS resources (EC2 instances, load balancers, Global Accelerators, and Lightsail instances) to find DNS entries pointing to non-existent or terminated resources.

**Key Benefits:**
- 🧹 **Clean DNS hygiene** - Remove dangling DNS records automatically
- 💰 **Cost optimization** - Identify unused resources that may incur costs  
- 🔍 **Security improvement** - Prevent subdomain takeover vulnerabilities
- 📊 **Infrastructure audit** - Get comprehensive visibility into your DNS-to-resource mapping

## How It Works

1. **Import DNS Records** - Extracts all DNS records from your specified Route 53 hosted zone
2. **Fetch AWS Resources** - Scans multiple AWS services across regions and accounts to inventory active resources
3. **Cross-Reference & Analyze** - Matches DNS records against actual resources to identify orphaned entries
4. **Generate Report** - Produces a detailed report showing stale DNS records with resource details

## Supported AWS Services

| Service | Status |
|---------|--------|
| ✅ EC2 | Supported |
| ✅ ELBv2 | Supported |
| ✅ Global Accelerator | Supported |
| ✅ Lightsail | Supported |
| ⏳ CloudFront | Planned |
| ⏳ Elastic Beanstalk | Planned |

## Demo Run

```bash
$ python3 app.py analyze 
record                    type               region     name
------------------------  -----------------  ---------  ---------------
mdminhazulhaque.io.       loadbalancer       us-east-2  prod-web-lb
demo.mdminhazulhaque.io.  instance           us-west-1  i-5a6b7c8d1100
api.mdminhazulhaque.io.   instance           us-west-2  i-5a6b7c8d1100
bob.mdminhazulhaque.io.   lightsail          us-west-1  bitnami-server
alice.mdminhazulhaque.io. instance           us-west-2  i-5a6b7c8d1100
foo.mdminhazulhaque.io.   instance           us-west-1  i-5a6b7c8d1100
bar.mdminhazulhaque.io.   globalaccelerator  us-west-2  prod-api-ga
baz.mdminhazulhaque.io.   loadbalancer       us-west-2  lb-baz
```

## Command Flow

Follow this command sequence for optimal results:

| Command | Description |
|---------|-------------|
| `python3 app.py import-dns` | 📥 Import Route 53 DNS records |
| `python3 app.py fetch-all` | 🔍 Scan AWS resources across accounts/regions |
| `python3 app.py analyze` | 📊 Cross-reference and generate stale DNS report |
| `python3 app.py clear-data` | 🗑️ Clear all cached data files (optional) |

## Advanced Configuration

### Filtering Options

Use `ignore_key` and `ignore_value` in config.ini to exclude certain DNS records:

```ini
[hostedzone]
# Skip DNS records containing these patterns in the name
ignore_key = vpn|dkim|_amazonses|_domainkey

# Skip DNS records containing these patterns in the value  
ignore_value = vpn|domainkey|google|microsoft|sendgrid|mailgun
```

### Multi-Account Setup

Configure multiple AWS profiles for cross-account scanning:

```ini
[search-profiles]
prod-account
dev-account  
staging-account
security-account
```

### Custom Regions

Specify which AWS regions to scan:

```ini
[search-regions]
us-east-1
us-west-2
eu-west-1
ap-southeast-1
```

## Quick Start

### Prerequisites

- **AWS CLI** configured with appropriate permissions
- **Python 3.7+** installed
- **AWS profiles** set up for target accounts
- **Route 53 access** to the hosted zone you want to audit

### Installation

```bash
# Clone the repository
git clone https://github.com/mdminhazulhaque/aws-stale-dns-finder.git
cd aws-stale-dns-finder

# Install dependencies
pip3 install -r requirements.txt

# Create configuration file
cp config.example.ini config.ini
```

### Configuration

Edit `config.ini` to match your environment:

```ini
[hostedzone]
hostedzoneid = /hostedzone/YOUR_ZONE_ID_HERE
profile = your-route53-profile
ignore_key = vpn|dkim|_amazonses
ignore_value = vpn|domainkey|google|microsoft|sendgrid

[search-profiles]
account-dev
account-prod
account-staging

[search-regions]
us-east-1
us-west-2
eu-west-1

[search-adapters]
ec2
elbv2
globalaccelerator
lightsail
```

### Usage

Run these commands in sequence:

```bash
# 1. Import DNS records from Route 53
python3 app.py import-dns

# 2. Fetch all AWS resources across accounts/regions
python3 app.py fetch-all

# 3. Analyze and generate stale DNS report
python3 app.py analyze

# Optional: Clear cached data for fresh run
python3 app.py clear-data
```

## Workflow

| Steps | Command |
|-------|---------|
| 📁 Create a valid config file named `config.ini` | `cp config.example.ini config.ini` |
| ⬇️ Import DNS records from Hosted Zone | `python3 app.py import-dns` |
| 🔄 Fetch Resources from All Accounts | `python3 app.py fetch-all` |
| 🔍 Prepare Report | `python3 app.py analyze` |
| ⚠️ Clear Cached Data | `python3 app.py clear-data` |

## Roadmap

### Planned Features
- [ ] **CloudFront integration** - Detect stale CloudFront distributions
- [ ] **Elastic Beanstalk support** - Include EB environment endpoints

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
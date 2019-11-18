# NoFrillsAdblocker
Basic DNS Adblocker w/ Unbound

***

Requires linux with unbound installed.
Use included unbound.conf file or add
```
include: "/etc/unbound/unbound.conf.d/adblock/*.conf"
```
to your existing unbound.conf file.

Run it manually, or run the script through your favourite job scheduler.

***

Running example...
```
~/$ sudo ./adblock-update.py

Blocklist Project - Ads
	:: URL Download: https://blocklist.site/app/dl/ads
	:: Parsing domains
		:: Stripping unnecessary sections
		:: Sorting domain list
		:: Parsed 135430 domains

Blocklist Project - Crypto
	:: URL Download: https://blocklist.site/app/dl/crypto
	:: Parsing domains
		:: Stripping unnecessary sections
		:: Sorting domain list
		:: Parsed 22327 domains

Total blocklist size: 157757

Checking configuration...
unbound-checkconf: no errors in /etc/unbound/unbound.conf

Restarting 'unbound' service...

~/$ 
```

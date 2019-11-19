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

```
usage: adblock-update [-h] [-q] [-f] [-Sh] [-Su] [-Au ALT_UNBOUND]
                      [-Ab ALT_BLOCKLIST] [-Ah ALT_HINTS_URL] [-u USER_AGENT]

optional arguments:
  -h,  --help                                       show this help message and exit
  -q,  --quiet                                      quiet output
  -f,  --force                                      force blocklist download
  -Sh, --skip-hints                                 skip root.hints download
  -Su, --skip-unbound                               skip unbound service update
  -Au ALT_UNBOUND,   --alt-unbound ALT_UNBOUND      use alternative unbound directory
  -Ab ALT_BLOCKLIST, --alt-blocklist ALT_BLOCKLIST  use alternative blocklist json file
  -Ah ALT_HINTS_URL, --alt-hints-url ALT_HINTS_URL  use alternative root hints url
  -u USER_AGENT,     --user-agent USER_AGENT        use a different user agent for downloads
```

***

Running example
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

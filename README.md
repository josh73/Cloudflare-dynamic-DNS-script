# Cloudflare-dynamic-DNS-script
A python script to update your dynamic IP address on Cloudflare
## Customization before use
Edit the file and update the following fields near the top of the script:

### Alert Mail Settings
>msg['From']    = 'xxxx@xxxx.com'                            # Change this<br>
>msg['To']      = 'xxxx@xxxx.com'                            # Change this<br>
>server = smtp('mail.xxxx.com', 587)                         # Change this<br>
>server.login('xxxx@xxxx.com', 'mypassword')                 # Change this<br>

### Cloudflare Account Settings
>auth_email          = "xxxx@xxxx.com"                         # Change this<br>
>auth_key            = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Change this. Found in cloudflare account settings<br>
>zone_name           = "mydomain.com"                          # Change this<br>
>record_name         = "mysubdomain.mydomain.com"              # Change this<br>

The **alert mail settings** set up your smtp mail server and mail account credentials to allow the script to send e-mail alerts in case of a failure.

The **Cloudflare account settings** set up your Cloudflare zone and account information. *record_name* is the subdomain you wish the script to update.

This script checks the domain ip address currently with cloudflare by polling cloudflare's dns server and comparing it against the current external IP address of the host running the script.

If there is no match an update is needed.

Before an update can be performed, **zone_identifier** and **record_identifier** are needed. They are cached in a file **cache.json**, located at the same directory as the script. If the file **cache.json** is missing or does not have the information, then **zone_identifier** and **record_identifier** are fetched from Cloudflare using Cloudflare API. They are tne saved in **cache.json**.

Once all the information is obtained, the Cloudflare API is used to update the subdomain IP address.

Logging is set up to go to the system syslog. Log level can be adjusted by changing the line:
> myLogger.setLevel(logging.INFO)<br>

to something else, for example:<br>

> myLogger.setLevel(logging.DEBUG)

### Running in the background
You can set this script to run every 10 minutes by adding the instruction to crontab:<br>
> */10 * * * * /path/to/script/cloudflare-dyn-dns-update.py

# Note
I am not associated with Cloudflare. I wrote this script on my own.


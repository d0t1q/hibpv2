#!/usr/bin/env python
# The version you're using was modified by Jeffrey Mustard. (https://github.com/JeffreyMustard)
# Original Author = Laurens Houben                          (https://github.com/houbbit)

# LinkedIN URL = https://www.linkedin.com/in/jeffrey-mustard-715884116


import requests
import time 
import argparse

parser = argparse.ArgumentParser(description="Verify if email address has been pwned")
parser.add_argument("-a", dest="address",
                  help="Single email address to be checked")
parser.add_argument("-f", dest="filename",
                  help="File to be checked with one email addresses per line")
args = parser.parse_args()

rate = 1.3                            # 1.3 seconds is a safe value that in most cases does not trigger rate limiting
server = "haveibeenpwned.com"         # Website to contact
sslVerify = True                      # Verify server certificate (set to False when you use a debugging proxy like BurpSuite)
proxies = {                           # Proxy to use (debugging)
#  'http': 'http://127.0.0.1:8080',    # Uncomment when needed
#  'https': 'http://127.0.0.1:8080',   # Uncomment when needed
}

# Set terminal ANSI code colors
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAILRED = '\033[91m'
ENDC = '\033[0m'

address = str(args.address)
filename = str(args.filename)
lstEmail = ["info@example.com","example@example.com"]

def main():
    if address != "None":
        checkAddress(address)
    elif filename != "None":
        email = [line.rstrip('\n') for line in open(filename)] # strip the newlines
        for email in email:
            checkAddress(email)
    else:
        for email in lstEmail:
            checkAddress(email)

def checkAddress(email):
    sleep = rate # Reset default acceptable rate
    check = requests.get("https://" + server + "/api/v2/breachedaccount/" + email + "?includeUnverified=true",
                 proxies = proxies,
                 verify = sslVerify)
    if str(check.status_code) == "404": # The address has not been breached.
        print OKGREEN + "[i] " + email + " has not been breached." + ENDC
        time.sleep(sleep) # sleep so that we don't trigger the rate limit
        return False
    elif str(check.status_code) == "200": # The address has been breached!
        print FAILRED + "[!] " + email + " has been breached!" + ENDC
        time.sleep(sleep) # sleep so that we don't trigger the rate limit
        return True
    elif str(check.status_code) == "429": # Rate limit triggered
        print WARNING + "[!] Rate limit exceeded, server instructed us to retry after " + check.headers['Retry-After'] + " seconds" + ENDC
        print WARNING + "    Refer to acceptable use of API: https://haveibeenpwned.com/API/v2#AcceptableUse" + ENDC
        sleep = float(check.headers['Retry-After']) # Read rate limit from HTTP response headers and set local sleep rate
        time.sleep(sleep) # sleeping a little longer as the server instructed us to do
        checkAddress(email) # try again
    else:
        print WARNING + "[!] Something went wrong while checking " + email + ENDC
        time.sleep(sleep) # sleep so that we don't trigger the rate limit
        return True

if __name__ == "__main__":
    main()

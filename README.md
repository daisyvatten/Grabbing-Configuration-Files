# Grabbing-Configuration-Files
Uses Netmiko module in Python

BEFORE USING !!! you will need to customize and change 1.) file paths 2.) Excel file information -- the excel file was used to pull IPs 3.) .env file with username and password 4.) 'secret' password (it is set to be the same as password password currently)
  Lines needing changes: 10 and 11 depending on whether or not same variable name is used in .env file; 26, 27, 84, 98, 107, 110 (file paths); 43 through 46 (Excel file information); 60 depending on device type; 64 (secret password, if different from password password)
 
IMPORTANT NOTE !!! switches will need "ip ssh password-auth" to work

Files are set to timeout after 3 days. This prevents buildup of files in case a hostname is changed, causing a new file to be created instead of overwriting previous file.
I did not test the timeout part, I am just assuming it works. Perhaps I shall update in 3 days. 
Update: works. I just made one mistake not putting in the full file path. 

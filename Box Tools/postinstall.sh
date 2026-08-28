#!/bin/zsh --no-rcs

# Install Box Tools

# Clear any pkg quarantine attributes
/usr/bin/find "$( /usr/bin/find /private/tmp -maxdepth 1 \( -iname \*\.pkg -o -iname \*\.mpkg \) )" -maxdepth 1 \( -iname \*\.pkg -o -iname \*\.mpkg \) -exec /usr/bin/xattr -cr {} +

# Work out current user. Abort install if one isn't present.
usernames=()
usernames+=( $( /usr/bin/dscl /Local/Default -list /Users uid | /usr/bin/awk '$2 >= 501 { print $1 }' | /usr/bin/grep -v -E "^(_|mfe)" ) )

# Go through and terminate all processes
processnames=('Box Helper.app' 'Box Edit.app' 'Box Device Trust.app' 'Box Local Com Server.app' 'Box Tools Custom Apps.app' 'Box.app')
for process in $processnames;
do
	pids=$( /bin/ps ax | /usr/bin/grep -i "$process" | /usr/bin/grep -v grep | /usr/bin/awk '{ print $1 }' )
	[ ! -z "$pids" ] && echo $pids | /usr/bin/xargs kill -9
	unset pids
done

# Find and install the pkg in that folder and install as the user
for account in $usernames;
do
	userid=$( /usr/bin/id -u $account )
	pkg=$( /usr/bin/find /private/tmp -maxdepth 1 \( -iname \*\.pkg -o -iname \*\.mpkg \) )
	/bin/rm -rf /Users/$account/Library/Application\ Support/Box/Box\ Edit
	/bin/launchctl asuser $userid sudo -iu $account /usr/sbin/installer -verboseR -target CurrentUserHomeDirectory -pkg $pkg
done

/bin/rm -rf ${pkg}

exit 0

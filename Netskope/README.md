## Netskope Client.

Original recipe inspiration: Patrick Gallagher's recipe - com.github.patgmac.download.Netskope

Replace the hostname in the TENANT field with your tenant name, and the variables will do the rest.

Download recipe just to get the latest admin deployable pkg.
PKG recipe to wrap the downloaded pkg with the tamper protection file and a highly custom postinstall script.
sign recipe to codesign the custom pkg from the PKG recipe.

See tech notes below:

Sign recipe to optionally codesign the created pkg.

Tech notes:

- Download client installer from pre-defined tenant URL. (Make an override of the PKG recipe to configure this.)
- Check signing signature of the downloaded pkg.
- Unpack pkg to a folder.
- Unpack a pkg in the decompressed folder to another folder. That gets us an .app we can work with.
- Get the version from that .app bundle
- Create a new pkg with custom post install script and tamper protection file
- THIS pkg recipe requires that a client id/secret be created in Jamf so it can read out the email address from the device record and auto register the install. Do not use this if using anything other than plist registration!
- Check the code signing
- Clean up temp folders
- Done!

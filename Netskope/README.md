## Netskope Client.

Original recipe inspiration: Patrick Gallagher's recipe - com.github.patgmac.download.Netskope

Replace the hostname in the HOSTNAME field with download-*hostnamehere*.goskope.com

Download recipe just to get the latest admin deployable pkg.

PKG recipe to properly download then version the file.

Tech notes:

- Download client installer from pre-defined tenant URL. (Make an override of the PKG recipe to configure this.)
- Check signing signature of the downloaded pkg.
- Unpack pkg to a folder.
- Unpack a pkg in the decompressed folder to another folder. That gets us an .app we can work with.
- Get the version from that .app bundle
- Version rename the original pkg file.
- Check the code signing
- Clean up temp folders
- Done!

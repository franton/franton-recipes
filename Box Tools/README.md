## Box Tools.

Download recipe just to get the latest admin deployable pkg from Box.

PKG recipe to properly version and wrap with a more admin friendly postinstall script.

Tech notes:

- Download from a fixed URL.
- Save pkg to a fixed filename.
- Decompress PKG to a folder. That gets us some of the internals.
- Decompress another PKG from our extract folder to another folder. That gets us the .app bundle.
- Read the version from the .app bundle
- Make a Scripts folder and a pkgroot folder. (For some reason best known to $DIETY anything involving pkg scripts HAS to be done this way.)
- Write a postinstall script from the pkg recipe into the Scripts folder.
- In pkgroot, write out a tmp folder then copy the downloaded pkg into it.
- Finally with all the env variables, make a deployable pkg containing the original plus the postinstall script.
- Done.

COMING SOON: Signing recipe!

## YubiKey Authenticator

Download recipe to get latest version from their github repo. Was based on Gerard Kok's recipe but reworked into YAML.

PKG recipe to properly version and package their app bundle.

Tech notes:

- Scan releases page for a specific format download URL.
- Get the version from that
- Save dmg with that version to a file.
- Check internal app signing to verify correct signature.
- Open and version the app bundle inside the dmg.
- Extract the app bundle to a folder
- Turn app bundle into a deployable pkg.
- Clean up files.
- Done.

COMING SOON: Signing recipe!

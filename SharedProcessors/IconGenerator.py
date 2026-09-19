#!/usr/local/autopkg/python
#
# Autopkg Copyright Greg Neagle, Timothy Sutton, Per Olofsson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# IconGenerator - Author: Richard Purves (with a LOT of code contributions from others)
# (since this project exists outside of the normal autopkg repo, i'm having to do bad copy paste code to make this work)
# so far dmgmounter has been partially copied (and modified to use diskutil). so has pkgcopier.
# eventually all this code bloat will go away.

import os
import os.path
import glob
import shutil
import subprocess

import plistlib

from autopkglib import Processor, ProcessorError
from autopkglib.DmgMounter import DmgMounter

__all__ = ["IconGenerator"]


class IconGenerator(Processor):
    description = ( "Creates app icon files in png format.",
                    "WARNING: This requires that SAP Icons be present on the mac this is",
                    "running on." )
    input_variables = {
        "file_path": {
            "required": True,
            "description": (
                "Path to the file to be processed."
                "Can point to a path inside a .dmg. This path may also contain "
                "basic globbing characters such as the wildcard '*', but only "
                "the first result will be returned."
            ),
        },
        "output_path": {
            "required": False,
            "description": (
                "Path to export the icon png files to."
                "Defaults to RECIPE_CACHE_DIR/os.path.basename(source_pkg)"
            ),
        },
        "size": {
            "required": False,
            "description": (
                "Resolution of exported png files."
                "e.g. 128 or 256 or 512 or 1024."
                "Default will be 512."
            ),
        }
    }
    output_variables = {
        "icon_path": {"description": "Path to generated png files."},
        "icon_summary_result": {
            "description": "Description of results."
        },
    }

    dmg_exts = [".dmg", ".iso", ".DMG", ".ISO"]

    __doc__ = description

    def __init__(self, data=None, infile=None, outfile=None):
        super().__init__(data, infile, outfile)
        self.mounts = dict()

    def parsePathForDMG(self, pathname):
        """Helper method for working with paths that reference something
        inside a disk image"""
        for extension in self.dmg_exts:
            dmg_path, dmg, dmg_source_path = pathname.partition(extension + "/")
            if dmg:
                dmg_path += extension
                return dmg_path, dmg, dmg_source_path
        # no disk image in path
        return pathname, "", ""

    def get_first_plist(self, text_string):
        """Gets the first plist from a text string that may contain one or
        more text-style plists.
        Returns a tuple - the first plist (if any) and the remaining
        string after the plist"""

        plist_header = "<?xml version"
        plist_footer = "</plist>"
        plist_start_index = text_string.find(plist_header)
        if plist_start_index == -1:
            # not found
            return ("", text_string)
        plist_end_index = text_string.find(
            plist_footer, plist_start_index + len(plist_header)
        )
        if plist_end_index == -1:
            # not found
            return ("", text_string)
        # adjust end value
        plist_end_index = plist_end_index + len(plist_footer)
        return (
            text_string[plist_start_index:plist_end_index],
            text_string[plist_end_index:],
        )
    
    def dmg_has_sla(self, dmgpath):
        """Returns true if dmg has a Software License Agreement.
        These dmgs normally cannot be attached without user intervention"""
        has_sla = False
        proc = subprocess.Popen(
            ["/usr/sbin/diskutil", "image", "info", "-plist", dmgpath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate()
        if stderr:
            # some error with hdiutil. Print it, but try to continue anyway.
            # (APFS disk images generate extraneous output to stderr)
            self.output(f"diskutil image info error {stderr} with image {dmgpath}.")

        pliststr, stdout = self.get_first_plist(stdout)
        if pliststr:
            try:
                plist = plistlib.loads(pliststr.encode())
                properties = plist.get("Properties")
                if properties:
                    has_sla = properties.get("Software License Agreement", False)
            except Exception:
                pass

        return has_sla
        
    def mount(self, pathname):
        """Mount image with disktuil."""
        # Make sure we don't try to mount something twice.
        if pathname in self.mounts:
            raise ProcessorError(f"{pathname} is already mounted")

        stdin = ""
        if self.dmg_has_sla(pathname):
            stdin = "Y\n"

        # Call diskutil.
        try:
            proc = subprocess.Popen(
                (
                    "/usr/sbin/diskutil",
                    "image",
                    "attach",
                    "--nobrowse",
                    "--plist",
                    pathname,
                ),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(stdin)
        except OSError as err:
            raise ProcessorError(
                f"diskutil execution failed with error code {err.errno}: {err.strerror}"
            )
        if proc.returncode != 0:
            raise ProcessorError(f"mounting {pathname} failed: {stderr}")

        # Read output plist.
        pliststr, stdout = self.get_first_plist(stdout)
        try:
            output = plistlib.loads(pliststr.encode())
        except Exception:
            raise ProcessorError(
                f"mounting {pathname} failed: unexpected output from diskutil"
            )

        # Find mount point.
        for part in output.get("system-entities", []):
            if "mount-point" in part:
                # Add to mount list.
                self.mounts[pathname] = part["mount-point"]
                self.output(f"Mounted disk image {pathname}")
                return self.mounts[pathname]
        raise ProcessorError(
            f"mounting {pathname} failed: unexpected output from diskutil"
        )

    def unmount(self, pathname) -> None:
        """Unmount previously mounted image."""

        # Don't try to unmount something we didn't mount.
        if pathname not in self.mounts:
            raise ProcessorError(f"{pathname} is not mounted")

        # Call disktuil.
        try:
            proc = subprocess.Popen(
                ("/usr/sbin/diskutil", "eject", "force", self.mounts[pathname]),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            _, stderr = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                f"diskutil execution failed with error code {err.errno}: {err.strerror}"
            )
        if proc.returncode != 0:
            raise ProcessorError(f"unmounting {pathname} failed: {stderr}")

        # Delete mount from mount list.
        del self.mounts[pathname]    

    def main(self):
        # Test for icons_cli presence. Not present means we fail out.
        icons_cli = shutil.which("icons_cli")

        if not icons_cli:
           sys.exit("Error: Required binary 'icons_cli' was not found.")
        
        # If size not specified then default to 512.
        size = self.env["size"]
        if size is None:
           size = 512
        
        # Clear any pre-existing summary
        if "icon_summary_result" in self.env:
            del self.env["icon_summary_result"]

        # Code shamelessly "borrowed" from Greg Neagles PkgCopier processor
        
        # Check if we're trying to copy something inside a dmg.
        dmg_path, dmg, dmg_source_path = self.parsePathForDMG(self.env["file_path"])
        try:
            if dmg:
                # Mount dmg and copy path inside.
                mount_point = self.mount(dmg_path)
                file_path = os.path.join(mount_point, dmg_source_path)
            else:
                # Straight copy from file system.
                file_path = self.env["file_path"]

            # Process the path for globs
            matches = glob.glob(file_path)
            matched_source_path = matches[0]
            if len(matches) > 1:
                self.output(
                    f"WARNING: Multiple paths match 'file_path' glob '{file_path}':"
                )
                for match in matches:
                    self.output(f"  - {match}")

            if [c for c in "*?[]!" if c in file_path]:
                self.output(
                    f"Using path '{matched_source_path}' matched from globbed "
                    f"'{file_path}'."
                )

            # Check that the source path ends with supported extension
            app_extensions = (".app")
            if os.path.splitext(matched_source_path)[1] not in app_extensions:
                raise ProcessorError(
                    "Source does not appear to be a app bundle based on its filename: "
                    f"'{matched_source_path}'"
                )

            # If output_path is not set, default to working folder.
            output_path = self.env.get("output_path") or os.path.join(
                self.env["RECIPE_CACHE_DIR"], os.path.basename(matched_source_path)
            )

            # Run the SAP icons binary with the supplied details
            result = subprocess.run(
                [icons_cli, "-s", size, "-i", file_path, "-o", output_path],
                capture_output=True,
                text=True,
                check=True,  # Raises CalledProcessError if the command fails
            )

            # Print output from the executable
            print("Output:", result.stdout)

        finally:
            if dmg:
                self.unmount(dmg_path)


if __name__ == '__main__':
    processor = IconGenerator()
    processor.execute_shell()

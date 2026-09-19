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
# IconGenerator - Author: Richard Purves (with code contributions from others)
#

import os
import os.path
import glob
import shutil
import subprocess

from autopkglib import Processor, ProcessorError
from autopkglib import DmgMounter

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

    __doc__ = description

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

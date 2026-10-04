#!/usr/local/autopkg/python
#
# Copyright 2026 Richard Purves
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


from datetime import datetime
import xml.etree.ElementTree as ET
import urllib.request

from autopkglib import Processor, ProcessorError

__all__ = ["S3XMLParser"]

class S3XMLParser(Processor):
    description = "Parses the XML from a download url"
    input_variables = {
        "url": {
            "required": True,
            "description": "URL to the xml file we need to parse for download links.",
        },
        "version": {
            "required": True,
            "description": (
                "Version of the software you are looking for."
                "e.g. 6.2.8"
            ),
        },
        "download_name": {
            "required": True,
            "description": (
                "Name of the file to download."
                "e.g. pkgname.pkg"
            ),
        },
    }
    output_variables = {
        "download_url": {"description": "Parsed url to the download file."}
    }

    __doc__ = description

    def main(self):
        # Get and check that needed variables exist
        
        url = self.env["url"]
        try:
            print(url)
        except NameError:
            raise ProcessorError(
                f"ERROR: url variable not set"
            )
            
        version = self.env["version"]
        try:
            print(version)
        except NameError:
            raise ProcessorError(
                f"ERROR: version variable not set"
            )

        download_name = self.env["download_name"]
        try:
            print(download_name)
        except NameError:
            raise ProcessorError(
                f"ERROR: download_name variable not set"
            )

        # Attempt to download xml for processing
        with urllib.request.urlopen(url) as content:
            response = content.read()
            root = ET.fromstring(response)
        
        # Extract S3 namespace if present
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"
        
        matching_files = []
        
        # Iterate over all Contents entries in bucket listing
        for content in root.findall(f"{ns}Contents"):
            key_elem = content.find(f"{ns}Key")
            last_modified_elem = content.find(f"{ns}LastModified")

            print("key elem: ", key_elem)
            print(type(key_elem))

            if key_elem is not None and key_elem.text:
                key_path = key_elem.text
                print(key_path)
                print(type(key_path))
            
            # Check if the entry matches our expected filename and version
            if key_path.endswith(download_name):
                last_modified_str = last_modified_elem.text if last_modified_elem is not None else ""

            print (last_modified_str)
            print(type(last_modified_str))
            
            # Parse ISO 8601 timestamp
            last_modified_dt = datetime.fromisoformat(
                last_modified_str.replace("Z", "+00:00")
            )
            print (last_modified_dt)
            print(type(last_modified_dt))

            # Passed checks. Append to variable.
            matching_files.append(
                {
                    "last_modified_dt": last_modified_dt,
                    "url": f"{url}/{key_path}"
                }
            )

        # We didnt find anything. Error here.
        if not matching_files:
            raise ProcessorError(
                f"ERROR: No matching files found"
            )

        # Find the latest LastModified date
        latest_file = max(matching_files, key=lambda x: x["last_modified_dt"])
        
        # Report out findings
        print(f"download_url: {latest_file['url']}")
        self.download_url = (f"{latest_file['url']}")

if __name__ == "__main__":
    processor = S3XMLParser()
    processor.execute_shell()

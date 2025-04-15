import os
import re
from pathlib import Path

# --- Configuration ---
SOURCE_FOLDER_NAME = "results"  # Name of the folder containing .md files
START_MARKER = "<!DOCTYPE html>"
END_MARKER = "</html>"
# Regex pattern to find the HTML block (case-insensitive for robustness)
# re.DOTALL makes '.' match newline characters
# The outer parentheses capture the entire block including markers
HTML_PATTERN = re.compile(
    f"({re.escape(START_MARKER)}.*?{re.escape(END_MARKER)})", 
    re.IGNORECASE | re.DOTALL
)
# --- End Configuration ---

def extract_last_html(source_dir: Path):
    """
    Finds markdown files in the source directory, extracts the last
    HTML block (DOCTYPE to /html), and saves it to a new .html file.
    """
    if not source_dir.is_dir():
        print(f"Error: Source directory '{source_dir}' not found or is not a directory.")
        return

    print(f"Starting extraction process in folder: '{source_dir}'")
    files_processed = 0
    html_files_created = 0

    # Iterate through items in the source directory
    for item_path in source_dir.iterdir():
        # Check if it's a file, ends with .md, and doesn't start with '.'
        if (item_path.is_file() and 
            item_path.suffix.lower() == ".md" and 
            not item_path.name.startswith('.')):

            files_processed += 1
            print(f"\nProcessing file: {item_path.name}")

            try:
                # Read the content of the markdown file
                content = item_path.read_text(encoding='utf-8')

                # Find all occurrences of the HTML pattern
                matches = HTML_PATTERN.findall(content)

                if matches:
                    # Get the last match found in the file
                    last_html_block = matches[-1]
                    print(f"  Found {len(matches)} HTML block(s). Extracting the last one.")

                    # Create the output filename (same name, .html extension)
                    output_html_path = item_path.with_suffix(".html")

                    try:
                        # Write the extracted HTML content to the new file
                        output_html_path.write_text(last_html_block, encoding='utf-8')
                        print(f"  Successfully created: {output_html_path.name}")
                        html_files_created += 1
                    except IOError as e:
                        print(f"  Error writing file {output_html_path.name}: {e}")
                    except Exception as e:
                         print(f"  An unexpected error occurred while writing {output_html_path.name}: {e}")

                else:
                    print(f"  No '{START_MARKER}...{END_MARKER}' block found in this file.")

            except FileNotFoundError:
                 print(f"  Error: File not found during processing (should not happen with is_file check): {item_path.name}")
            except IOError as e:
                print(f"  Error reading file {item_path.name}: {e}")
            except Exception as e:
                 print(f"  An unexpected error occurred while processing {item_path.name}: {e}")


    print(f"\n--------------------------------------------------")
    print(f"Processing finished.")
    print(f"Total Markdown files scanned: {files_processed}")
    print(f"Total HTML files created: {html_files_created}")
    print(f"--------------------------------------------------")

# --- Main Execution ---
if __name__ == "__main__":
    source_directory = Path(SOURCE_FOLDER_NAME)
    extract_last_html(source_directory)
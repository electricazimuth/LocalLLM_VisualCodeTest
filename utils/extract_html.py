import re
from pathlib import Path

# --- Configuration ---
SOURCE_FOLDER_NAME = "results/2026.02.04/results"  # Name of the folder containing .md files
OUTPUT_FOLDER_NAME = "results/2026.02.04/html"     # Name of the folder to save extracted HTML files

# Define the closing tag pattern separately for clarity and robustness
# Allows optional whitespace before the closing >
END_TAG_PATTERN = r"</html\s*>"
# Use a user-friendly version for messages
END_MARKER_DISPLAY = "</html>"

# Updated Regex pattern to find the HTML block:
# - Optionally starts with <!DOCTYPE html...> followed by optional whitespace.
# - Must contain <html...> tag (allowing attributes).
# - Ends with </html[whitespace]?> tag.
# - Case-insensitive and DOTALL (matches newlines).
# - Outer parentheses capture the entire matched block.
HTML_PATTERN = re.compile(
    # Capture group for the whole block
    r"(" +
    # Optional non-capturing group for DOCTYPE (allowing attributes) and whitespace
    # Matches "<!DOCTYPE html" optionally followed by any chars except '>' ([^>]*), then '>',
    # followed by zero or more whitespace chars (\s*)
    # The whole group is made optional by the final '?'
    r"(?:<!DOCTYPE html[^>]*>\s*)?" +
    # Opening <html> tag: matches '<html', a word boundary (\b),
    # then any characters except '>' ([^>]*), then '>'
    r"<html\b[^>]*>" +
    # Non-greedy match for anything in between (. matches newline due to DOTALL)
    r".*?" +
    # The defined end tag pattern (NOT escaped, we want its regex meaning)
    END_TAG_PATTERN +
    # End capture group
    r")",
    re.IGNORECASE | re.DOTALL
)

# --- Default HTML Boilerplate for No Results ---
# (Using END_MARKER_DISPLAY for user-facing text)
NO_RESULT_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No Valid Result</title>
    <style>
        body {{ font-family: sans-serif; padding: 2em; }}
        h1 {{ color: #cc0000; }}
    </style>
</head>
<body>
    <h1>No Valid Result</h1>
    <p>Could not find a valid HTML block in the source file.</p>
</body>
</html>
"""
# --- End Configuration ---

def extract_last_html(source_dir: Path, output_dir: Path):
    """
    Finds markdown files in the source directory. For each file, it attempts
    to extract the last HTML block (matching robust criteria).
    It ALWAYS creates an output .html file in the output directory:
    - If a match is found, the output file contains the extracted HTML.
    - If no match is found, the output file contains a default "No Valid Result" HTML page.
    """
    if not source_dir.is_dir():
        print(f"Error: Source directory '{source_dir}' not found or is not a directory.")
        return

    # Ensure the output directory exists, create if not
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory '{output_dir}' ensured.")
    except OSError as e:
        print(f"Error: Could not create output directory '{output_dir}': {e}")
        return # Stop if we can't create the output folder

    print(f"\nStarting processing from folder: '{source_dir}'")
    files_processed = 0
    html_files_created = 0
    files_with_errors = 0

    # Iterate through items in the source directory
    for item_path in source_dir.iterdir():
        # Check if it's a file, ends with .md, and doesn't start with '.'
        if (item_path.is_file() and
            item_path.suffix.lower() == ".md" and
            not item_path.name.startswith('.')):

            files_processed += 1
            print(f"\nProcessing file: {item_path.name}")

            # Determine output path regardless of match success
            output_filename = item_path.stem + ".html"
            output_html_path = output_dir / output_filename
            content_to_write = None
            match_found = False

            try:
                # Read the content of the markdown file
                content = item_path.read_text(encoding='utf-8')

                # Find all occurrences of the HTML pattern
                # Use search() instead of findall() if we only expect one block or always want the first large block
                # Sticking with findall() and taking the last match is often safer for benchmark logs
                # where the result might be appended after other attempts or logs.
                matches = HTML_PATTERN.findall(content)

                if matches:
                    # Get the last match found in the file
                    # matches[-1] will be the content from the outer capture group
                    content_to_write = matches[-1]
                    match_found = True
                    print(f"  Found {len(matches)} HTML block(s). Using the last one.")
                else:
                    # No match found, prepare the default boilerplate
                    content_to_write = NO_RESULT_HTML
                    # Use the display marker in the message
                    print(f"  No valid HTML block (matching pattern ending with {END_MARKER_DISPLAY}) found. Preparing default 'No Result' HTML.")

            except FileNotFoundError:
                 print(f"  Error: Source file not found during processing: {item_path.name}")
                 files_with_errors += 1
                 continue # Skip to the next file
            except IOError as e:
                print(f"  Error reading file {item_path.name}: {e}")
                files_with_errors += 1
                continue # Skip to the next file
            except Exception as e:
                 print(f"  An unexpected error occurred while processing {item_path.name}: {e}")
                 files_with_errors += 1
                 continue # Skip to the next file

            # --- Write the output file (either extracted content or boilerplate) ---
            if content_to_write is not None:
                try:
                    output_html_path.write_text(content_to_write, encoding='utf-8')
                    # Display the relative path to the created file
                    status = "extracted content" if match_found else "default content"
                    print(f"  Successfully created: {output_html_path} (with {status})")
                    html_files_created += 1
                except IOError as e:
                    print(f"  Error writing file {output_html_path}: {e}")
                    files_with_errors += 1
                except Exception as e:
                     print(f"  An unexpected error occurred while writing {output_html_path}: {e}")
                     files_with_errors += 1
            else:
                # This case should ideally not be reached if reading logic is correct,
                # but included for completeness.
                print(f"  Skipping write for {output_html_path} due to prior processing error.")
                files_with_errors += 1


    print(f"\n--------------------------------------------------")
    print(f"Processing finished.")
    print(f"Source directory scanned: '{source_dir}'")
    print(f"Output directory: '{output_dir}'")
    print(f"Total Markdown files scanned: {files_processed}")
    print(f"Total HTML files created/updated: {html_files_created}")
    if files_with_errors > 0:
        print(f"Files skipped due to read/write errors: {files_with_errors}")
    print(f"--------------------------------------------------")

# --- Main Execution ---
if __name__ == "__main__":
    # Source directory (relative to script location or CWD)
    source_directory = Path(SOURCE_FOLDER_NAME)
    # Output directory (relative to where the script is run - CWD)
    output_directory = Path(OUTPUT_FOLDER_NAME)

    extract_last_html(source_directory, output_directory)
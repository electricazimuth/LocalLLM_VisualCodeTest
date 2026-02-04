import os
import re
import json
import html

# --- Configuration ---
PROMPTS_DIR = 'code_prompts'
RESULTS_DIR = 'results/2026.02.04/html/'
RESULTS_LOCAL_PATH = 'html/'
OUTPUT_FILENAME = 'results/2026.02.04/index.html'

# Define the intended original dimensions of the content within the HTML results
IFRAME_ORIGINAL_WIDTH = 800
IFRAME_ORIGINAL_HEIGHT = 650
IFRAME_SCALE = 0.666

# --- Helper Functions ---

def get_test_types(prompts_dir):
    """Scans the prompts directory to determine valid test types."""
    types = []
    
    if not os.path.isdir(prompts_dir):
        print(f"Error: Prompts directory not found: {prompts_dir}")
        return {'error': f"Prompts directory '{html.escape(prompts_dir)}' not found."}

    try:
        files = os.listdir(prompts_dir)
    except OSError as e:
        return {'error': f"Error reading prompts directory: {e}"}

    found_files = False
    for file in files:
        if file.startswith('.'):
            continue
        
        # Get filename without extension
        type_name = os.path.splitext(file)[0]
        if type_name:
            types.append(type_name)
            found_files = True

    types.sort()

    if not found_files:
        return {'error': f"No valid prompt files found in '{html.escape(prompts_dir)}'."}
    
    # Empty types list but dir exists is handled by logic above, return what we have
    return {'types': types}

def parse_result_filename(filename, valid_types):
    """Parses a filename against the regex pattern and valid types."""
    if not valid_types:
        return None

    # Build regex dynamically: ^(.*?)_(TYPE1|TYPE2|...)_(\d{8}_\d{6})\.html$
    # re.escape ensures characters like '+' or '.' in type names don't break regex
    types_regex = '|'.join(map(re.escape, valid_types))
    
    pattern = rf'^(.*?)_({types_regex})_(\d{{8}}_\d{{6}})\.html$'
    
    match = re.match(pattern, filename, re.IGNORECASE)
    if match:
        captured_type = match.group(2)
        # Double check existence (though regex logic essentially guarantees it)
        if captured_type in valid_types:
            return {
                'model': match.group(1),
                'type': captured_type,
                'timestamp': match.group(3),
                'filename': filename
            }
    return None

def get_all_results(results_dir, valid_types):
    """Scans results directory and groups files by type."""
    all_results = {}
    initial_error_message = None

    if not valid_types:
        return {'results': [], 'error': None}

    if not os.path.isdir(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        return {'results': [], 'error': f"Results directory '{html.escape(results_dir)}' not found."}

    # Initialize groups
    for t in valid_types:
        all_results[t] = []

    try:
        result_files = os.listdir(results_dir)
    except OSError as e:
        return {'results': [], 'error': f"Error reading results directory: {e}"}

    for file in result_files:
        if file.startswith('.'):
            continue

        parsed = parse_result_filename(file, valid_types)
        if parsed:
            if parsed['type'] in all_results:
                all_results[parsed['type']].append(parsed)

    # Sort results by model name
    for t in all_results:
        all_results[t].sort(key=lambda x: x['model'])

    return {'results': all_results, 'error': initial_error_message}

def safe_json_dump(data):
    """
    Serialize data to JSON and escape characters to be safe for embedding 
    inside HTML <script> tags (replicates PHP JSON_HEX_* flags).
    """
    json_str = json.dumps(data)
    # Replace unsafe characters for HTML embedding
    json_str = json_str.replace('<', '\\u003c') \
                       .replace('>', '\\u003e') \
                       .replace('&', '\\u0026') \
                       .replace("'", '\\u0027')
    return json_str

# --- Main Logic ---

def main():
    # Get Types
    types_data = get_test_types(PROMPTS_DIR)
    available_types = types_data.get('types', [])
    generation_error = types_data.get('error', None)

    results_data = {}
    all_results = {}

    # Get Results
    if not generation_error and available_types:
        results_data = get_all_results(RESULTS_DIR, available_types)
        all_results = results_data.get('results', {})
        
        # Append error if specific result scan failed
        if results_data.get('error'):
            current_err = generation_error + '<br>' if generation_error else ''
            generation_error = current_err + results_data['error']
    elif not generation_error and not available_types:
        generation_error = "No test types found, cannot scan for results."

    # Calculate dimensions
    container_width = IFRAME_ORIGINAL_WIDTH * IFRAME_SCALE
    container_height = IFRAME_ORIGINAL_HEIGHT * IFRAME_SCALE

    # Prepare Data object
    json_data = {
        'types': available_types,
        'results': all_results,
        'config': {
            'resultsDir': RESULTS_LOCAL_PATH,
            'iframeOriginalWidth': IFRAME_ORIGINAL_WIDTH,
            'iframeOriginalHeight': IFRAME_ORIGINAL_HEIGHT,
            'iframeScale': IFRAME_SCALE,
            'containerWidth': container_width,
            'containerHeight': container_height
        },
        'generationError': generation_error
    }

    json_string = safe_json_dump(json_data)

    # --- Generate HTML ---
    # We construct the HTML parts here to inject into the template
    
    # 1. Navigation HTML
    nav_html_parts = []
    if available_types:
        for t in available_types:
            nav_html_parts.append(f'<a href="#" data-type="{html.escape(t)}">{html.escape(t)}</a>')
        nav_html_content = "\n".join(nav_html_parts)
    else:
        nav_html_content = '<span id="no-types-message">No test types found.</span>'

    # 2. CSS variables injection (handled by Python formatting)
    # 3. Full Template
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coding Test Viewer</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 15px;
            background-color: #f4f4f4;
        }
        h1, h2 {
            color: #333;
            margin-top: 0;
        }
        .nav {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #eee;
            border-radius: 5px;
        }
        .nav strong {
            margin-right: 10px;
        }
        .nav a {
            text-decoration: none;
            color: #007bff;
            margin: 0 5px;
            padding: 5px 8px;
            border-radius: 3px;
            transition: background-color 0.2s ease, color 0.2s ease;
            cursor: pointer;
        }
        .nav a:hover {
            background-color: #ddd;
            color: #0056b3;
        }
        .nav a.selected {
            font-weight: bold;
            background-color: #007bff;
            color: white;
        }
        .error {
            color: red;
            background-color: #fee;
            border: 1px solid red;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        #results-container {
            margin-top: 20px;
        }
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(calc(var(--container-width, __CONTAINER_WIDTH__px) + 10px), 1fr));
            gap: 20px;
            margin-top: 10px;
        }
        .iframe-container {
            border: 1px solid #ccc;
            background-color: #fff;
            padding: 5px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }
        .iframe-container .label {
            font-size: 0.8em;
            color: #555;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            min-height: 1.2em;
            font-weight: bold;
        }
        .iframe-wrapper {
            width: var(--container-width, __CONTAINER_WIDTH__px);
            height: var(--container-height, __CONTAINER_HEIGHT__px);
            overflow: hidden;
            position: relative;
            margin: 0 auto;
        }
        .scaled-iframe {
            width: var(--iframe-original-width, __ORIG_WIDTH__px);
            height: var(--iframe-original-height, __ORIG_HEIGHT__px);
            border: none;
            transform: scale(var(--iframe-scale, __SCALE__));
            transform-origin: 0 0;
            position: absolute;
            top: 0;
            left: 0;
        }
        .info-message {
            margin-top: 20px;
            padding: 15px;
            background-color: #eef;
            border: 1px solid #ccd;
            border-radius: 5px;
            color: #336;
        }
    </style>
</head>
<body>

    <h1>Coding Test Results</h1>

    <div id="generation-error-display" class="error" style="display: none;"></div>

    <div class="nav" id="type-navigation">
        <strong>Select Test Type:</strong>
        __NAV_CONTENT__
    </div>

    <div id="results-container">
         <p class="info-message" id="initial-message">Please select a test type above to view results.</p>
    </div>

    <!-- Embed the JSON data -->
    <script id="app-data" type="application/json">
        __JSON_STRING__
    </script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const appDataElement = document.getElementById('app-data');
            const navContainer = document.getElementById('type-navigation');
            const resultsContainer = document.getElementById('results-container');
            const generationErrorDisplay = document.getElementById('generation-error-display');
            const initialMessage = document.getElementById('initial-message');

            if (!appDataElement) {
                console.error("App data script tag not found!");
                resultsContainer.innerHTML = '<p class="error">Critical error: Application data is missing.</p>';
                return;
            }

            let appData;
            try {
                appData = JSON.parse(appDataElement.textContent);
            } catch (e) {
                console.error("Failed to parse app data JSON:", e);
                resultsContainer.innerHTML = '<p class="error">Critical error: Could not parse application data.</p>';
                return;
            }

            // --- Apply CSS Variables from Config ---
            const root = document.documentElement;
            root.style.setProperty('--iframe-original-width', `${appData.config.iframeOriginalWidth}px`);
            root.style.setProperty('--iframe-original-height', `${appData.config.iframeOriginalHeight}px`);
            root.style.setProperty('--iframe-scale', appData.config.iframeScale);
            root.style.setProperty('--container-width', `${appData.config.containerWidth}px`);
            root.style.setProperty('--container-height', `${appData.config.containerHeight}px`);

            // --- Display Generation Errors ---
            if (appData.generationError) {
                generationErrorDisplay.innerHTML = appData.generationError;
                generationErrorDisplay.style.display = 'block';
            }
            
            // Check if types exist for initial message logic
            if (appData.types.length === 0 && !appData.generationError) {
                 if(initialMessage) initialMessage.style.display = 'none';
            } else if (appData.types.length > 0 && initialMessage) {
                initialMessage.style.display = 'block';
            }

            // --- Function to Display Results ---
            function displayResults(type) {
                resultsContainer.innerHTML = '';
                 if (initialMessage) initialMessage.style.display = 'none';

                const links = navContainer.querySelectorAll('a');
                links.forEach(link => {
                    if (link.dataset.type === type) {
                        link.classList.add('selected');
                    } else {
                        link.classList.remove('selected');
                    }
                });

                const results = appData.results[type];
                const config = appData.config;

                const title = document.createElement('h2');
                title.textContent = `Results for: ${type}`;
                resultsContainer.appendChild(title);

                if (results && results.length > 0) {
                    const grid = document.createElement('div');
                    grid.className = 'results-grid';

                    results.forEach(result => {
                        const container = document.createElement('div');
                        container.className = 'iframe-container';

                        const label = document.createElement('div');
                        label.className = 'label';
                        label.textContent = result.model;
                        label.title = result.model;
                        container.appendChild(label);

                        const wrapper = document.createElement('div');
                        wrapper.className = 'iframe-wrapper';

                        const iframe = document.createElement('iframe');
                        iframe.className = 'scaled-iframe';
                        iframe.src = `${config.resultsDir}/${result.filename}`;
                        iframe.loading = 'lazy';
                        iframe.title = `Result for ${result.model}`;

                        wrapper.appendChild(iframe);
                        container.appendChild(wrapper);
                        grid.appendChild(container);
                    });
                    resultsContainer.appendChild(grid);
                } else {
                    const noResultsMessage = document.createElement('p');
                    noResultsMessage.className = 'info-message';
                    noResultsMessage.textContent = `No results found for this test type in '${config.resultsDir}'.`;
                    resultsContainer.appendChild(noResultsMessage);
                }
            }

            // --- Attach Event Listeners ---
            navContainer.addEventListener('click', function(event) {
                if (event.target.tagName === 'A' && event.target.dataset.type) {
                    event.preventDefault();
                    const selectedType = event.target.dataset.type;
                    displayResults(selectedType);
                }
            });
        });
    </script>
</body>
</html>"""

    # Perform Replacements
    # Note: We use string replace instead of f-strings for the main template 
    # to avoid conflicting with CSS braces {}
    output_html = html_template.replace('__CONTAINER_WIDTH__', str(container_width)) \
                               .replace('__CONTAINER_HEIGHT__', str(container_height)) \
                               .replace('__ORIG_WIDTH__', str(IFRAME_ORIGINAL_WIDTH)) \
                               .replace('__ORIG_HEIGHT__', str(IFRAME_ORIGINAL_HEIGHT)) \
                               .replace('__SCALE__', str(IFRAME_SCALE)) \
                               .replace('__NAV_CONTENT__', nav_html_content) \
                               .replace('__JSON_STRING__', json_string)

    # --- Write Output File ---
    output_path = os.path.join(os.getcwd(), OUTPUT_FILENAME)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        print(f"Successfully generated static file: {OUTPUT_FILENAME}")
    except OSError as e:
        print(f"Error: Failed to write static file to {output_path}")
        print(e)

if __name__ == "__main__":
    main()
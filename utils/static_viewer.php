<?php
// --- Configuration ---
define('PROMPTS_DIR', 'prompts');
define('RESULTS_DIR', 'html');
define('OUTPUT_FILENAME', 'static_viewer.html'); // Name of the static file to create
// Define the intended original dimensions of the content within the HTML results
// We need this to size the iframe container correctly for the scale
define('IFRAME_ORIGINAL_WIDTH', 800);
define('IFRAME_ORIGINAL_HEIGHT', 650);
define('IFRAME_SCALE', 0.666);

// --- End Configuration ---

// --- Helper Functions ---
function get_test_types(string $promptsDir): array {
    $types = [];
    if (!is_dir($promptsDir)) {
        error_log("Prompts directory not found: " . $promptsDir);
        return ['error' => "Prompts directory '" . htmlspecialchars($promptsDir) . "' not found."];
    }
    $files = scandir($promptsDir);
    $foundFiles = false;
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') {
            continue;
        }
        $type = pathinfo($file, PATHINFO_FILENAME);
        if (!empty($type)) {
            $types[] = $type;
            $foundFiles = true;
        }
    }
    sort($types);

    if (!$foundFiles && is_dir($promptsDir)) {
         return ['error' => "No valid prompt files found in '" . htmlspecialchars($promptsDir) . "'."];
    }
     if (empty($types) && !is_dir($promptsDir)) {
         // This case is already handled by the initial check, but kept for clarity
         return ['error' => "Prompts directory '" . htmlspecialchars($promptsDir) . "' not found."];
    }
    return ['types' => $types];
}

function parse_result_filename(string $filename, array $validTypes): ?array {
    if (empty($validTypes)) return null; // No types to match against

    // Build the regex dynamically based on discovered valid types
    $typesRegex = implode('|', array_map('preg_quote', $validTypes));

    // Regex breakdown:
    // ^(.*?)_         : Capture model name (non-greedy) - Group 1
    // ($typesRegex)_   : Capture one of the valid types - Group 2
    // (\d{8}_\d{6})   : Capture timestamp (YYYYMMDD_HHMMSS) - Group 3
    // \.html$         : Match .html at the end
    // i               : Case-insensitive
    if (preg_match('/^(.*?)_(' . $typesRegex . ')_(\d{8}_\d{6})\.html$/i', $filename, $matches)) {
        // Double check the captured type just in case regex was too broad (unlikely here)
        if (in_array($matches[2], $validTypes, true)) {
             return [
                'model' => $matches[1],
                'type' => $matches[2],
                'timestamp' => $matches[3],
                'filename' => $filename
            ];
        }
    }
    return null;
}

function get_all_results(string $resultsDir, array $validTypes): array {
    $allResults = [];
    $initialErrorMessage = null;

    if (empty($validTypes)) {
        return ['results' => [], 'error' => null]; // No types, so no results possible
    }

    if (!is_dir($resultsDir)) {
        error_log("Results directory not found: " . $resultsDir);
        return ['results' => [], 'error' => "Results directory '" . htmlspecialchars($resultsDir) . "' not found."];
    }

    // Initialize result groups for all valid types
    foreach ($validTypes as $type) {
        $allResults[$type] = [];
    }

    $result_files = scandir($resultsDir);
    $foundResults = false;

    foreach ($result_files as $file) {
        if ($file === '.' || $file === '..') continue;

        $parsed = parse_result_filename($file, $validTypes);

        if ($parsed !== null) {
            // Ensure the type key exists (it should from initialization)
            if (array_key_exists($parsed['type'], $allResults)) {
                 $allResults[$parsed['type']][] = $parsed;
                 $foundResults = true;
            } else {
                // This case should ideally not happen if $validTypes is correct
                 error_log("Parsed result type '{$parsed['type']}' not found in initial list.");
            }
        }
    }

    // Sort results within each type by model name
    foreach ($allResults as $type => &$results_for_type) {
        usort($results_for_type, fn($a, $b) => strcmp($a['model'], $b['model']));
    }
    unset($results_for_type); // Unset reference

    // Optional: Check if any results were found *at all* across valid types
    if (!$foundResults && is_dir($resultsDir)) {
         // You might want a specific message if the directory exists but contains no *matching* files
         // $initialErrorMessage = "No result files matching the expected format found in '" . htmlspecialchars($resultsDir) . "'.";
         // Or just let the per-type messages handle it.
    }


    return ['results' => $allResults, 'error' => $initialErrorMessage];
}

// --- Main Logic ---
$typesData = get_test_types(PROMPTS_DIR);
$available_types = $typesData['types'] ?? [];
$generation_error = $typesData['error'] ?? null;

$resultsData = [];
$all_results = [];

if (!$generation_error && !empty($available_types)) {
    $resultsData = get_all_results(RESULTS_DIR, $available_types);
    $all_results = $resultsData['results'];
    // Append results error if prompts dir was okay but results dir is not
    if ($resultsData['error']) {
        $generation_error = ($generation_error ? $generation_error . '<br>' : '') . $resultsData['error'];
    }
} elseif (!$generation_error && empty($available_types)) {
    // This state is covered by get_test_types error handling, but as a fallback:
     $generation_error = "No test types found, cannot scan for results.";
}


// Calculate scaled dimensions for the container
$container_width = IFRAME_ORIGINAL_WIDTH * IFRAME_SCALE;
$container_height = IFRAME_ORIGINAL_HEIGHT * IFRAME_SCALE;

// --- Prepare Data for JSON Embedding ---
$jsonData = [
    'types' => $available_types,
    'results' => $all_results,
    'config' => [
        'resultsDir' => RESULTS_DIR,
        'iframeOriginalWidth' => IFRAME_ORIGINAL_WIDTH,
        'iframeOriginalHeight' => IFRAME_ORIGINAL_HEIGHT,
        'iframeScale' => IFRAME_SCALE,
        'containerWidth' => $container_width,
        'containerHeight' => $container_height
    ],
    'generationError' => $generation_error // Pass errors encountered during generation
];

// Use options for safer embedding in <script>
$jsonString = json_encode($jsonData, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);

// --- Start Generating HTML Output ---
ob_start(); // Start output buffering
?>
<!DOCTYPE html>
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
            margin-top: 0; /* Adjust spacing */
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
            cursor: pointer; /* Indicate clickable */
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
            /* Use CSS variable for dynamic width */
            grid-template-columns: repeat(auto-fill, minmax(calc(var(--container-width, <?= $container_width ?>px) + 10px), 1fr));
            gap: 20px; /* Spacing between grid items */
            margin-top: 10px; /* Space below h2 */
        }
        .iframe-container {
            border: 1px solid #ccc;
            background-color: #fff;
            padding: 5px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex; /* Use flexbox for internal alignment */
            flex-direction: column; /* Stack label above iframe wrapper */
        }
        .iframe-container .label {
            font-size: 0.8em;
            color: #555;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            min-height: 1.2em; /* Ensure space even if label is short */
            font-weight: bold;
        }
        .iframe-wrapper {
            /* Use CSS variables */
            width: var(--container-width, <?= $container_width ?>px);
            height: var(--container-height, <?= $container_height ?>px);
            overflow: hidden;
            position: relative;
            margin: 0 auto;
        }
        .scaled-iframe {
             /* Use CSS variables */
            width: var(--iframe-original-width, <?= IFRAME_ORIGINAL_WIDTH ?>px);
            height: var(--iframe-original-height, <?= IFRAME_ORIGINAL_HEIGHT ?>px);
            border: none;
            transform: scale(var(--iframe-scale, <?= IFRAME_SCALE ?>));
            transform-origin: 0 0;
            position: absolute;
            top: 0;
            left: 0;
        }
        /* Style for messages when no type is selected or no results found */
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
        <?php if (!empty($available_types)): ?>
            <?php foreach ($available_types as $type): ?>
                <a href="#" data-type="<?= htmlspecialchars($type) ?>">
                    <?= htmlspecialchars($type) ?>
                </a>
            <?php endforeach; ?>
        <?php else: ?>
            <span id="no-types-message">No test types found.</span>
        <?php endif; ?>
    </div>

    <div id="results-container">
        <!-- Results will be dynamically inserted here -->
         <p class="info-message" id="initial-message">Please select a test type above to view results.</p>
    </div>

    <!-- Embed the JSON data -->
    <script id="app-data" type="application/json">
        <?= $jsonString ?>
    </script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const appDataElement = document.getElementById('app-data');
            const navContainer = document.getElementById('type-navigation');
            const resultsContainer = document.getElementById('results-container');
            const generationErrorDisplay = document.getElementById('generation-error-display');
            const initialMessage = document.getElementById('initial-message');
            const noTypesMessage = document.getElementById('no-types-message');

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
                generationErrorDisplay.innerHTML = appData.generationError; // Use innerHTML as error might contain <br>
                generationErrorDisplay.style.display = 'block';
            }

             // --- Handle No Types Found during generation ---
             if (appData.types.length === 0 && !appData.generationError) {
                // If types array is empty, but no specific error was logged for it,
                // ensure the "No types found" message is visible.
                if(initialMessage) initialMessage.style.display = 'none'; // Hide initial prompt
                 if(noTypesMessage) noTypesMessage.style.display = 'inline'; // Show "no types" span
            } else if (appData.types.length > 0 && initialMessage) {
                initialMessage.style.display = 'block'; // Show initial prompt if types exist
            }


            // --- Function to Display Results ---
            function displayResults(type) {
                // Clear previous results and hide initial message
                resultsContainer.innerHTML = '';
                 if (initialMessage) initialMessage.style.display = 'none';

                // Update navigation links style
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
                title.textContent = `Results for: ${type}`; // Security: type comes from our generated data, considered safe
                resultsContainer.appendChild(title);

                if (results && results.length > 0) {
                    const grid = document.createElement('div');
                    grid.className = 'results-grid';

                    results.forEach(result => {
                        const container = document.createElement('div');
                        container.className = 'iframe-container';

                        const label = document.createElement('div');
                        label.className = 'label';
                        label.textContent = result.model; // Security: model comes from our generated data
                        label.title = result.model;
                        container.appendChild(label);

                        const wrapper = document.createElement('div');
                        wrapper.className = 'iframe-wrapper';

                        const iframe = document.createElement('iframe');
                        iframe.className = 'scaled-iframe';
                        // Security: Ensure resultsDir and filename don't allow directory traversal if manipulated
                        // Since this runs client-side based on server-generated data, primary risk is XSS if data is bad.
                        // Filenames are parsed strictly, RESULTS_DIR is a define. htmlspecialchars was used server-side.
                        iframe.src = `${config.resultsDir}/${result.filename}`;
                        iframe.loading = 'lazy';
                        iframe.title = `Result for ${result.model}`; // Security: model comes from our generated data

                        wrapper.appendChild(iframe);
                        container.appendChild(wrapper);
                        grid.appendChild(container);
                    });
                    resultsContainer.appendChild(grid);
                } else {
                    const noResultsMessage = document.createElement('p');
                     noResultsMessage.className = 'info-message'; // Use consistent styling
                    noResultsMessage.textContent = `No results found for this test type in '${config.resultsDir}'.`;
                    resultsContainer.appendChild(noResultsMessage);
                }
            }

            // --- Attach Event Listeners ---
            navContainer.addEventListener('click', function(event) {
                if (event.target.tagName === 'A' && event.target.dataset.type) {
                    event.preventDefault(); // Prevent default anchor behavior
                    const selectedType = event.target.dataset.type;
                    displayResults(selectedType);
                }
            });

             // --- Optional: Display first type automatically on load ---
             /*
             if (appData.types && appData.types.length > 0) {
                 displayResults(appData.types[0]);
             }
             */
            // By default, it will show the "Please select..." message until a type is clicked.

        });
    </script>

</body>
</html>
<?php
// --- Get buffered HTML content ---
$htmlContent = ob_get_clean();

// --- Write to Static File ---
$outputFilePath = __DIR__ . '/' . OUTPUT_FILENAME; // Assume output in the same dir as the script
if (file_put_contents($outputFilePath, $htmlContent)) {
    echo "Successfully generated static file: " . htmlspecialchars(OUTPUT_FILENAME) . "\n";
} else {
    echo "Error: Failed to write static file to " . htmlspecialchars($outputFilePath) . "\n";
    // Consider adding more error details if possible (e.g., permissions)
    error_log("Failed to write static file: " . $outputFilePath . " - Check permissions.");
}

?>
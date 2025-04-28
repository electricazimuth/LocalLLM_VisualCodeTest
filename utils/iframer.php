<?php
// --- Configuration ---
define('PROMPTS_DIR', 'prompts');
define('RESULTS_DIR', 'html');
// Define the intended original dimensions of the content within the HTML results
// We need this to size the iframe container correctly for the 50% scale
define('IFRAME_ORIGINAL_WIDTH', 800); // Adjust if your tests render wider/narrower
define('IFRAME_ORIGINAL_HEIGHT', 650); // Adjust if your tests render taller/shorter
define('IFRAME_SCALE', 0.666); 

// --- End Configuration ---

// --- Helper Functions ---
function get_test_types(string $promptsDir): array {
    $types = [];
    if (!is_dir($promptsDir)) {
        return $types; // Return empty if dir doesn't exist
    }
    $files = scandir($promptsDir);
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') {
            continue;
        }
        // Use pathinfo to reliably get the filename without extension
        $type = pathinfo($file, PATHINFO_FILENAME);
        if (!empty($type)) {
            $types[] = $type;
        }
    }
    sort($types); // Keep them alphabetical
    return $types;
}

function parse_result_filename(string $filename, array $validTypes): ?array {
    // Regex breakdown:
    // ^(.*)_          : Capture model name (non-greedy) - Group 1
    // ([a-z0-9_]+)_   : Capture the type (lowercase letters, numbers, underscore) - Group 2
    // (\d{8}_\d{6})   : Capture timestamp (YYYYMMDD_HHMMSS) - Group 3
    // \.html$         : Match .html at the end
    // i               : Case-insensitive (though types seem lowercase)
    if (preg_match('/^(.*?)_(' . implode('|', array_map('preg_quote', $validTypes)) . ')_(\d{8}_\d{6})\.html$/i', $filename, $matches)) {
        // Check if the captured type is actually one of the known valid types
        // The regex already restricts this, but double-checking doesn't hurt
        $type = $matches[2];
        if (in_array($type, $validTypes, true)) {
            return [
                'model' => $matches[1],
                'type' => $type,
                'timestamp' => $matches[3],
                'filename' => $filename
            ];
        }
    }
    return null; // Return null if it doesn't match the pattern or valid type
}

// --- Main Logic ---
$available_types = get_test_types(PROMPTS_DIR);
$selected_type = null;
$error_message = '';
$results_for_type = [];

if (isset($_GET['type'])) {
    if (in_array($_GET['type'], $available_types, true)) {
        $selected_type = $_GET['type'];
    } else {
        $error_message = "Invalid test type specified.";
    }
}

// Scan results directory only if a valid type is selected
if ($selected_type && is_dir(RESULTS_DIR)) {
    $result_files = scandir(RESULTS_DIR);
    foreach ($result_files as $file) {
        if ($file === '.' || $file === '..') continue;

        $parsed = parse_result_filename($file, $available_types);

        if ($parsed !== null && $parsed['type'] === $selected_type) {
            $results_for_type[] = $parsed;
        }
    }
    // Optional: Sort results, e.g., by model name
    usort($results_for_type, fn($a, $b) => strcmp($a['model'], $b['model']));

} elseif ($selected_type && !is_dir(RESULTS_DIR)) {
     $error_message = "Results directory '" . htmlspecialchars(RESULTS_DIR) . "' not found.";
} elseif (empty($available_types) && is_dir(PROMPTS_DIR)) {
     $error_message = "No valid prompt files found in '" . htmlspecialchars(PROMPTS_DIR) . "'.";
} elseif (!is_dir(PROMPTS_DIR)) {
     $error_message = "Prompts directory '" . htmlspecialchars(PROMPTS_DIR) . "' not found.";
}

// Calculate scaled dimensions for the container
$container_width = IFRAME_ORIGINAL_WIDTH * IFRAME_SCALE;
$container_height = IFRAME_ORIGINAL_HEIGHT * IFRAME_SCALE;

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coding Test Viewer<?= $selected_type ? ' - ' . htmlspecialchars($selected_type) : '' ?></title>
    <style>
        body {
            font-family: sans-serif;
            margin: 15px;
            background-color: #f4f4f4;
        }
        h1, h2 {
            color: #333;
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
            transition: background-color 0.2s ease;
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
        .results-grid {
            display: grid;
            /* Adjust columns based on how many fit */
            grid-template-columns: repeat(auto-fill, minmax(<?= $container_width + 10 /* Add padding/border */ ?>px, 1fr));
            gap: 20px; /* Spacing between grid items */
            margin-top: 20px;
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
            /* This div takes the size of the SCALED iframe */
            width: <?= $container_width ?>px;
            height: <?= $container_height ?>px;
            overflow: hidden; /* Hide the parts of the scaled iframe outside this box */
            position: relative; /* Needed for transform-origin */
            margin: 0 auto; /* Center the wrapper if grid cell is wider */
        }
        .scaled-iframe {
            /* Set the iframe's logical size to its ORIGINAL dimensions */
            width: <?= IFRAME_ORIGINAL_WIDTH ?>px;
            height: <?= IFRAME_ORIGINAL_HEIGHT ?>px;
            border: none;
            /* Scale down to 50% */
            transform: scale(<?= IFRAME_SCALE ?>);
            /* Anchor the scaling to the top-left corner */
            transform-origin: 0 0;
             /* Ensure it aligns correctly within the wrapper */
            position: absolute;
            top: 0;
            left: 0;
        }
    </style>
</head>
<body>

    <?php if ($error_message): ?>
        <p class="error"><?= $error_message ?></p>
    <?php endif; ?>

    <div class="nav">
        <strong>Select Test Type:</strong>
        <?php if (!empty($available_types)): ?>
            <?php foreach ($available_types as $type): ?>
                <a href="?type=<?= urlencode($type) ?>"
                   class="<?= ($type === $selected_type) ? 'selected' : '' ?>">
                    <?= htmlspecialchars($type) ?>
                </a>
            <?php endforeach; ?>
        <?php else: ?>
            <span>No test types found in '<?= htmlspecialchars(PROMPTS_DIR) ?>'.</span>
        <?php endif; ?>
    </div>

    <?php if ($selected_type && empty($error_message)): ?>
        <h2>Results for: <?= htmlspecialchars($selected_type) ?></h2>

        <?php if (!empty($results_for_type)): ?>
            <div class="results-grid">
                <?php foreach ($results_for_type as $result): ?>
                    <div class="iframe-container">
                        <div class="label" title="<?= htmlspecialchars($result['model']) ?>">
                            <?= htmlspecialchars($result['model']) ?>
                        </div>
                        <div class="iframe-wrapper">
                            <iframe class="scaled-iframe"
                                    src="<?= htmlspecialchars(RESULTS_DIR . '/' . $result['filename']) ?>"
                                    loading="lazy"
                                    title="Result for <?= htmlspecialchars($result['model']) ?>">
                            </iframe>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <p>No results found for this test type in '<?= htmlspecialchars(RESULTS_DIR) ?>'.</p>
        <?php endif; ?>

    <?php elseif (!$selected_type && empty($error_message)): ?>
        <p>Please select a test type above to view results.</p>
    <?php endif; ?>

</body>
</html>
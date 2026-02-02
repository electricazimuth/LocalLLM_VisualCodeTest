# LocalLLM Visual Code Test
Javascript Benchmarking Local LLMs using Llamacpp / Koboldcpp

# View the current results
This is the output from the current prompts.  
* [Results 2026.01.26](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2026.01.26/)
* [Results 2026.01.20](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2026.01.20/)
* [Results 2025.08.06](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2025.08.06/)
* [Results 2025.08.04](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2025.08.04/)
* [Results 2025.04.28](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2025.04.28/)
* [Results 2025.04.21](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2025.04.21/)
* [Results 2025.04.15](https://electricazimuth.github.io/LocalLLM_VisualCodeTest/results/2025.04.15/)


#  Visual LLM Benchmark 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional: Add a license badge if you have one -->

**Ready to unleash the power of your local Large Language Models? 🔥**

This project provides a powerful and flexible Python suite to systematically benchmark multiple `.gguf` language models running locally via the fantastic [KoboldCpp](https://github.com/LostRuins/koboldcpp) backend. Pit your models against each other using your custom prompts (especially geared towards JavaScript generation in this setup!) and see how they perform head-to-head on *your* hardware!

Stop guessing, start measuring! 📊

## ✨ Features ✨

*   **🤖 Automated Benchmarking:** Set it up and let it run! The script iterates through your models and prompts automatically.
*   **⚙️ Seamless KoboldCpp Integration:** Automatically launches, manages, waits for, and shuts down KoboldCpp instances for each model, ensuring a clean testing environment.
*   **📂 Dynamic Discovery:** Just point the script to your model and prompt directories – it finds all compatible `.gguf` files and `.md` prompts.
*   **⏱️ Robust API Handling:** Uses the KoboldCpp API, including smart timeouts and a fallback mechanism (`/api/extra/generate/check`) to capture results even from long-running generations.
*   **🧠 Model-Specific Tuning:** Easily apply custom API parameters (`model_payload_filter`) or add specific instructions to prompts (`model_prompt_filter`) based on the model being tested.
*   **✅ Smart Skipping:** Already have results for a model/prompt pair? The script intelligently skips them, making it easy to resume interrupted benchmarks or add new tests.
*   **📄 Detailed Markdown Results:** Saves the raw output for each model/prompt combination into a clearly named `.md` file in the `results` directory. Includes generation time appended as an HTML comment (`<!-- 123.45s -->`).
*   **👁️ HTML Output Extraction:** Includes a handy utility (`extract_html.py`) to automatically find and extract `<!DOCTYPE html>...</html>` blocks from your result files into separate, viewable `.html` files – perfect for checking generated web pages!
*   **🔧 Highly Configurable:** Easily adjust paths, KoboldCpp launch arguments (GPU layers, context size, etc.), API parameters, timeouts, model size filters, and more!
*   **⚠️ Graceful Error Handling & Reporting:** Captures errors, logs failures, provides a final summary, and handles Ctrl+C interruptions gracefully.

##  (How it Works)

1.  **Configure:** Set your paths and KoboldCpp settings in `run_benchmarks.py`.
2.  **Discover:** The script scans your specified directories for `.gguf` models (within size limits) and `.md` prompt files.
3.  **Launch & Loop:**
    *   For each model found:
        *   It **launches** a dedicated KoboldCpp instance with the specified arguments and the current model.
        *   It **waits** for the KoboldCpp server and model to be fully loaded and ready.
        *   For each prompt found:
            *   It checks if results already **exist**. If so, it skips.
            *   It reads the prompt content and applies any **model-specific filters**.
            *   It constructs the API **payload**, applying model-specific parameters.
            *   It sends the generation request to the KoboldCpp **API**.
            *   If the request **times out**, it attempts a **fallback** check to retrieve partial results.
            *   It **saves** the generated text (plus timing info) to a unique `.md` file in the `results` directory.
    *   It **shuts down** the KoboldCpp instance for the current model.
    *   It waits briefly before starting the **next** model.
4.  **Extract (Optional):** Run `extract_html.py` to scan the `results` folder and pull out any complete HTML blocks into `.html` files for easy browser viewing.

##  Getting Started 

### Prerequisites

*   **Python 3:** Make sure you have Python 3 installed.
*   **KoboldCpp:** You need a working installation of KoboldCpp. Get it [here](https://github.com/LostRuins/koboldcpp).
*   **Models:** `.gguf` format LLM files you want to benchmark.
*   **Prompts:** `.md` files containing the prompts you want to test. (This setup is particularly focused on prompts designed to elicit JavaScript code).


### Setup & Configuration

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/electricazimuth/LocalLLM_VisualCodeTest.git # Replace with your repo URL
    cd LocalLLM_VisualCodeTest
    ```

2.  **❗ Configure `config.py` ❗:** Update the paths for your setup. Open `config.py` in a text editor and **carefully update the following paths and settings** near the top of the file:
    *   `KOBOLDCPP_SCRIPT`: **Absolute path** to your `koboldcpp.py` script.
    *   `MODEL_DIR`: **Absolute path** to the directory containing your `.gguf` models.
    *   `PROMPT_DIR`: **Absolute path** to the directory containing your `.md` prompt files.
    *   `RESULTS_DIR`: Path where the benchmark results (`.md` files) will be saved.
    *   `KOBOLDCPP_ARGS`: **Crucial!** Adjust these arguments for your hardware and KoboldCpp setup.
        *   Pay special attention to `--usecublas` (or `--useclblast`, etc.) and GPU layer settings (`--gpulayers`). Ensure the `--port` matches the `API_URL`.
        *   **Tip:** Start with conservative settings (e.g., fewer GPU layers) and increase if stable.
    *   `MAX_SIZE_BYTES` / `MIN_SIZE_BYTES`: Filter models by file size if needed.
    *   `API_PAYLOAD_TEMPLATE`: Modify default generation parameters (temperature, top_p, max_length, etc.) if desired.
    *   `SERVER_STARTUP_WAIT`: Increase if your models take longer to load.
    *   `PRIMARY_API_TIMEOUT`: Increase if you expect very long generation times.

3.  **Prepare Your Models & Prompts:** Ensure your `.gguf` files are in the `MODEL_DIR` and your `.md` prompt files are in the `PROMPT_DIR`.

##  Usage 

### Running the Benchmarks

1.  Navigate to the project directory in your terminal.
2.  Execute the main script eg(backend is either "llamacpp" or "koboldcpp"):
    ```bash
    python run_benchmarks.py --backend llamacpp
    ```
3.  **For long runs**, it's highly recommended to use `nohup` (on Linux/macOS) to prevent the process from stopping if you close the terminal:
    ```bash
    nohup python run_benchmarks.py > runbench.log 2>&1 &
    ```
    This will run the script in the background and log all output to `runbench.log`. You can monitor the log using `tail -f runbench.log`.

4.  Watch the console (or log file) for progress updates! The script will print which model and prompt it's currently processing, timings, and any errors.

### Extracting HTML Results

1.  After the benchmarks have generated some `.md` files in your `results` directory (ensure this directory exists and contains results).
2.  Make sure `extract_html.py` is configured correctly (the `SOURCE_FOLDER_NAME` should match your `RESULTS_DIR` name, default is "results").
3.  Run the extraction script from the project root directory:
    ```bash
    python extract_html.py
    ```
4.  Check your `results` directory – you should now see corresponding `.html` files for any markdown files that contained valid `<!DOCTYPE html>...</html>` blocks. Open them in your browser!
5.  Generate a static viewer use the `static_viewer.php`

## 📊 Results Interpretation

*   Benchmark results are saved as individual `.md` files in the directory specified by `RESULTS_DIR`.
*   The filename format is: `model-stem_prompt-stem_timestamp[_fallback].md`
    *   `model-stem`: Name of the model file (without extension).
    *   `prompt-stem`: Name of the prompt file (without extension).
    *   `timestamp`: Date and time of generation (YYYYMMDD_HHMMSS).
    *   `_fallback` (Optional): Indicates the result was obtained using the fallback API call after a timeout.
*   Each file contains the raw text output generated by the model.
*   An HTML comment `<!-- [TIME]s -->` (e.g., `<!-- 15.23s -->`) is appended to the *end* of the generated content, indicating the time taken for the API generation request (or time until timeout).

## 🛠️ Customization & Filtering

*   **Model Filtering:** Modify the filtering logic within the `run_benchmarks.py` script (search for `MAX_SIZE_BYTES`, `MIN_SIZE_BYTES`, and commented-out name filters) to include/exclude specific models based on name patterns or size.
*   **Prompt Filtering:** Add similar logic if you need to filter prompts.
*   **Model-Specific Settings:** Use the `model_payload_filter` and `model_prompt_filter` functions in `run_benchmarks.py` to tweak API parameters or add instructions tailored to specific models (e.g., adjusting temperature for 'qwen' models as shown in the example).


---

Happy Benchmarking! 🎉
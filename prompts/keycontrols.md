You are an expert javascript and html coder.

# Keyboard Controlled Character Webgame

*   **Goal:** Using HTML, JS and CSS create a webpage with a moovable character using input handling (keyboard events), state management (e.g., moving left/right), updating position, basic sprite animation (optional).
*   **Task:** Create a simple character (a rectangle is fine) that can be moved left and right using arrow keys or WASD. Prevent the character from moving off-screen. Optionally, make it look like it's facing the direction it's moving.
*   **Requirements:**
    1.  Define a "Player" object/structure with position (x, y), size (width, height), and speed.
    2.  Set up keyboard event listeners (`keydown`, `keyup`) to track which movement keys are currently pressed.
    3.  In the game loop:
        *   Check the state of the movement keys.
        *   Update the player's x-position based on the pressed keys and the player's speed. (Using delta time for frame-rate independent movement is a plus).
        *   Implement boundary checks to keep the player within the canvas width.
        *   Draw the player (e.g., as a rectangle).
    4.  Optional Animation:
        *   If moving left, draw an indicator (like an "eye") on the left side of the rectangle.
        *   If moving right, draw the indicator on the right side.
        *   If idle, perhaps center the indicator or remove it.
*   **Visual Goal:** A rectangle at the bottom of the screen that moves left and right when keys are pressed, stopping at the edges. Optionally, a small visual cue indicates its facing direction.

**Functional Requirements:** 
1. Add jumping
2. Implement acceleration/deceleration 
3. Handle multiple key presses simultaneously (e.g., diagonal movement)

**Desirable Features:** Correct event listener setup and state management for key presses, smooth movement logic, accurate boundary checks, clear code structure.

# Deliverable

The page must run directly in a modern web browser without external physics engines or utility libraries (plain JavaScript and Canvas API only).
A single HTML file with the code added, use the following boilerplate html. If you want to add notes to your response add them into the section#notes area in the html page.
```
<!DOCTYPE html>
<html>
<head>
    <title>Run and Jump</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { border: 1px solid black; background-color: #fff; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // --- YOUR CODE GOES HERE ---

        function gameLoop(timestamp) {
            // Clear canvas (usually needed)
            // ctx.clearRect(0, 0, W, H);

            // --- Update logic ---

            // --- Draw logic ---

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        // requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
    
    </section>
</body>
</html>
```

 
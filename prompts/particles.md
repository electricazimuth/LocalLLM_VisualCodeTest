You are an expert javascript and html coder.

# Simple Particle Emitter Webgame

**Goal:** 
Create a particle emitter using html, js and css. Use javascript best practice for object creation/management, rendering loop, basic physics/movement, state update per object.

**Task:** 
Create a simple particle emitter that spawns particles from a central point on mouse click. Particles should have a limited lifespan, move outwards with random velocity, and fade out.

**Requirements:**  
1.  Store particles in an array.  
2.  On canvas click, create 10-20 new particles at the click location.  
3.  Each particle should have:  
    *   Position (x, y)  
    *   Velocity (vx, vy) - random initial direction/speed.
    *   Lifespan (e.g., 1-3 seconds).
    *   Color (can be fixed or randomized).
    *   Size (e.g., 2-5 pixels).
4.  In the game loop:
    *   Update each particle's position based on its velocity.
    *   Decrease each particle's lifespan (using delta time is a bonus point).
    *   Remove particles whose lifespan has run out.
    *   Draw each particle (e.g., as a small circle or square).
    *   Optional: Implement fading (reduce alpha based on remaining lifespan).
    *   Optional: Add simple gravity effect (modify `vy` each frame).

**Visual Goal:**  
Clicking on the canvas spawns a burst of small dots that move outwards and disappear after a short time.

**Functional Requirements:**  
Optimize this to allow thousands of particles. 
Ensure delta time is handled correctly for smooth animations.
Make the emission continuous while the mouse is held down.

**Desirable Features:**   
Make good use of arrays, object/class structure for particles, correct loop for update/draw, removing elements from an array while iterating, use animation best practices.

# Deliverable
The page must run directly in a modern web browser without external physics engines or utility libraries (plain JavaScript and Canvas API only).
A single HTML file with the code added, use the following boilerplate html. If you want to add notes to your response add them into the section#notes area in the html page.
```
<!DOCTYPE html>
<html>
<head>
    <title>Particle Emitter</title>
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
    
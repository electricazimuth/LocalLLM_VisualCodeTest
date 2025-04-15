You are an expert javascript and html coder.

# Simple Aiming and Firing Mechanism Webgame

**Goal:** Using HTML, JS and CSS create a standalone webpage game that has mouse input handling (position, clicks), vector math (calculating direction), object creation/management (projectiles).  
**Task:** Create a "turret" (a simple shape at a fixed position) that aims towards the mouse cursor. When the mouse is clicked, fire a projectile from the turret towards the cursor's position at that moment.  
**Requirements:**
1.  Define a "Turret" position (e.g., bottom center of the canvas).
2.  Define a "Projectile" object/class with position, velocity, size, and color.
3.  Store active projectiles in an array.
4.  Track the mouse cursor's position relative to the canvas.
5.  In the game loop:
    *   Calculate the angle from the turret to the mouse cursor (`Math.atan2` is useful here).
    *   Draw the turret (e.g., a base rectangle and a rotating "barrel" line/rectangle pointing towards the mouse).
    *   Update the position of each active projectile based on its velocity.
    *   Remove projectiles that go off-screen.
    *   Draw all active projectiles.
6.  Set up a mouse click event listener:
    *   On click, calculate the direction vector from the turret to the click position.
    *   Normalize this vector and multiply by a desired projectile speed to get the velocity (vx, vy).
    *   Create a new projectile instance with this velocity, starting at the turret's position (or end of its barrel).
    *   Add the new projectile to the array.  

**Visual Goal:** A shape at the bottom aims a line towards the mouse. Clicking fires a small dot/circle from the shape along that line, which continues moving until off-screen.

**Functional Requirements:** 
1. Limit the firing rate (cooldown)
2. Implement projectile lifespan
3. Handle collision detection between projectiles and potential targets

**Desirable Features:** 
Correct use of mouse event listeners, understanding of basic trigonometry/vector math for aiming (`atan2`, `cos`, `sin`, normalization), object pooling awareness (for follow-up), array management.

# Deliverable

The html page must run directly in a modern web browser without external physics engines or utility libraries (plain JavaScript and Canvas API only).
Respond with a single HTML file with your code added, use the following boilerplate html. If you want to add notes to your response add them into the section#notes area in the html page.
```
<!DOCTYPE html>
<html>
<head>
    <title>Turret Shooting</title>
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
    
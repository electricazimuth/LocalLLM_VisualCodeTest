You are an expert javascript and html coder.

# Autonomous Fireworks Particle Simulation

**Goal:**
Create an autonomous fireworks simulation using HTML, JS, and CSS. Demonstrate javascript best practices for object creation/management, rendering loop, physics simulation (gravity, explosion), state update per object, and managing different object types.

**Task:**
Develop a simple simulation that automatically launches "fireworks" from the bottom of the canvas. Each firework should travel upwards, explode at a certain height, and produce a burst of colorful particles that fall realistically under gravity and fade out.

**Requirements:**
1.  **Particle Management:** Store all active particles (rockets and explosion fragments) efficiently, likely in a single array.
2.  **Autonomous Launching:** Periodically launch new "firework rockets" from the bottom-center area of the canvas at random intervals (e.g., every 0.5 to 2 seconds).
3.  **Firework Rocket:**
    *   Represents the initial projectile.
    *   Has Position (x, y) starting near the bottom.
    *   Has Velocity (vx, vy) - primarily upwards (`vy` is negative), with slight horizontal randomness.
    *   Affected by Gravity (its upward velocity should decrease over time).
    *   Has a "fuse" time or target altitude for explosion (e.g., explodes after 1-2 seconds or upon reaching a certain height/velocity slowdown).
    *   May have a simple visual representation (e.g., a bright streak or dot).
    *   On explosion, the rocket particle is removed.
4.  **Explosion Particles:**
    *   Created when a firework rocket explodes (e.g., 30-80 particles per explosion).
    *   Spawn at the rocket's explosion location.
    *   Have diverse initial Velocities (vx, vy) - radiating outwards randomly.
    *   Affected by Gravity (should realistically arc and fall).
    *   Have a Lifespan (e.g., 1-3 seconds).
    *   Have Color (randomized, potentially based on the rocket).
    *   Have Size (e.g., 2-4 pixels).
5.  **Game Loop (`requestAnimationFrame`):**
    *   Calculate delta time for smooth, frame-rate independent animation.
    *   **Update Logic:**
        *   Handle autonomous launching of new rockets based on timers.
        *   Update each particle's position based on its velocity and delta time.
        *   Apply gravity effect to *all* particles (modify `vy`).
        *   Check rocket "fuses" or explosion conditions. Trigger explosions (remove rocket, create explosion particles).
        *   Decrease explosion particle lifespans based on delta time.
        *   Remove particles whose lifespan has run out or rockets that have exploded. Optimize removal from the array.
    *   **Draw Logic:**
        *   Clear the canvas (consider a dark background for better contrast).
        *   Draw each particle (rockets and explosion fragments).
        *   Implement fading for explosion particles (reduce alpha based on remaining lifespan).

**Visual Goal:**
The canvas should show streaks rising from the bottom, bursting into colorful showers of sparks that realistically fall under gravity and fade away, creating a continuous, dynamic fireworks display effect. A dark background (`#000` or `#222`) is recommended. Pay attention to the canvas size and make the fireworks and explosions proportional to the size of the screen, they should travel at least half the height of the canvas and the explosions should be 20 - 30% of the width and height of the canvas.

**Functional Requirements:**
*   Optimize the simulation to handle potentially hundreds or thousands of particles smoothly.
*   Ensure delta time is correctly implemented for consistent animation speed regardless of frame rate.
*   The fireworks should launch automatically without any user interaction.

**Desirable Features:**
*   Good use of object/class structure (e.g., potentially separate classes or distinct properties for `Rocket` and `ExplosionParticle`).
*   Clean separation of update and draw logic.
*   Efficient array management, especially when removing particles.
*   Use of `requestAnimationFrame` for the main loop.
*   Consider subtle variations in firework types (e.g., different colors, explosion sizes, launch heights).

# Deliverable
The page must run directly in a modern web browser without external physics engines or utility libraries (plain JavaScript and Canvas API only).
A single HTML file with the code added, use the following boilerplate html. If you want to add notes to your response add them into the section#notes area in the html page.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; } /* Dark background suggested */
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; } /* Dark canvas bg */
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
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

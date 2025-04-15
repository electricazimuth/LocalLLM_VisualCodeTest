```html
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

        const player = {
            x: W / 2,
            y: H - 50,
            width: 50,
            height: 50,
            speed: 5,
            vx: 0,
            vy: 0,
            isJumping: false,
            gravity: 0.5
        };

        const keys = {
            left: false,
            right: false,
            up: false
        };

        document.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    keys.left = true;
                    break;
                case 'ArrowRight':
                case 'd':
                    keys.right = true;
                    break;
                case 'ArrowUp':
                case 'w':
                    if (!player.isJumping) {
                        keys.up = true;
                        player.isJumping = true;
                        player.vy = -10; // Apply an upward velocity
                    }
                    break;
            }
        });

        document.addEventListener('keyup', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    keys.left = false;
                    break;
                case 'ArrowRight':
                case 'd':
                    keys.right = false;
                    break;
                case 'ArrowUp':
                case 'w':
                    keys.up = false;
                    break;
            }
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Horizontal Movement
            if (keys.left) {
                player.vx = -player.speed;
            } else if (keys.right) {
                player.vx = player.speed;
            } else {
                player.vx = 0; // Stop if no keys pressed
            }

            // Vertical Movement (Jumping and Gravity)
            player.vy += player.gravity;
            player.y += player.vy;

            // Apply Boundary Checks
            if (player.x + player.width > W) {
                player.x = W - player.width;
            } else if (player.x < 0) {
                player.x = 0;
            }

            if (player.y + player.height > H) {
                player.y = H - player.height;
                player.isJumping = false;
                player.vy = 0; // Reset vertical velocity on landing
            }

            // Draw the player
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <h2>Notes:</h2>
        <ul>
            <li>This code implements basic movement with WASD or Arrow keys.</li>
            <li>Jumping is added with an upward velocity and gravity.</li>
            <li>Boundary checks prevent the player from going off-screen.</li>
            <li>The animation is simple (a blue rectangle).</li>
        </ul>
    </section>
</body>
</html>

```

**Explanation:**

1. **Player Object:**

   - The `player` object stores the character's position (`x`, `y`), size (`width`, `height`), speed, velocity (`vx`, `vy`), jumping state (`isJumping`), and gravity.

2. **Key Event Listeners:**

   - `keydown` and `keyup` event listeners track which arrow keys or WASD keys are pressed.

3. **Game Loop:**
   - `requestAnimationFrame(gameLoop)` creates a smooth animation loop.

4. **Movement Logic:**

   - **Horizontal:** If left or right is pressed, set the horizontal velocity (`player.vx`). Otherwise, set it to 0 to stop.
   - **Vertical (Jumping & Gravity):** Apply gravity (`player.gravity`) to the vertical velocity (`player.vy`). When the `up` key is pressed and the player is not already jumping, apply an upward impulse (`player.vy = -10`).

5. **Boundary Checks:**

   - Prevent the player from moving beyond the canvas edges.

6. **Drawing:**

   - A simple blue rectangle is drawn at the player's position.

**Next Steps:**

- **Animation:** Add more visual elements to indicate direction (e.g., eyes on the sides).
- **Collision Detection:** Add logic to detect collisions with other objects.
- **Level Design:** Create a game map with obstacles and platforms.
 <!-- 102.31s -->
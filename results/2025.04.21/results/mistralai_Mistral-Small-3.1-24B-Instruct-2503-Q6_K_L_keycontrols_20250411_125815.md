Below is a complete implementation of the described web game using HTML, JavaScript, and CSS. This code includes the necessary elements to move the character left and right using arrow keys or WASD, handle jumping, implement acceleration and deceleration, and ensure smooth movement and boundary checks.

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
            acceleration: 0.5,
            deceleration: 0.8,
            velocityX: 0,
            velocityY: 0,
            gravity: 0.5,
            jumpForce: 10,
            isJumping: false,
            facingRight: true
        };

        const keys = {
            left: false,
            right: false,
            up: false,
            down: false,
            w: false,
            a: false,
            s: false,
            d: false
        };

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
            if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
            if (e.key === 'ArrowUp' || e.key === 'w') {
                keys.up = true;
                if (!player.isJumping) {
                    player.velocityY = -player.jumpForce;
                    player.isJumping = true;
                }
            }
            if (e.key === 'ArrowDown' || e.key === 's') keys.down = true;
        });

        document.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
            if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
            if (e.key === 'ArrowUp' || e.key === 'w') keys.up = false;
            if (e.key === 'ArrowDown' || e.key === 's') keys.down = false;
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Update logic
            if (keys.left || keys.a) {
                if (player.velocityX > -player.speed) {
                    player.velocityX -= player.acceleration;
                }
                player.facingRight = false;
            }
            if (keys.right || keys.d) {
                if (player.velocityX < player.speed) {
                    player.velocityX += player.acceleration;
                }
                player.facingRight = true;
            }

            if (!(keys.left || keys.a) && !(keys.right || keys.d)) {
                player.velocityX *= player.deceleration;
            }

            if (player.isJumping) {
                player.velocityY += player.gravity;
                if (player.y + player.height >= H) {
                    player.y = H - player.height;
                    player.velocityY = 0;
                    player.isJumping = false;
                }
            }

            player.x += player.velocityX;
            player.y += player.velocityY;

            // Boundary checks
            if (player.x < 0) player.x = 0;
            if (player.x + player.width > W) player.x = W - player.width;

            // Draw logic
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            // Optional: Draw indicator for facing direction
            if (player.facingRight) {
                ctx.fillStyle = 'red';
                ctx.fillRect(player.x + player.width, player.y + player.height / 2 - 5, 10, 10);
            } else {
                ctx.fillStyle = 'red';
                ctx.fillRect(player.x - 10, player.y + player.height / 2 - 5, 10, 10);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <!-- Notes -->
        <!-- 1. The player object contains properties for position, size, speed, velocity, and state (e.g., jumping). -->
        <!-- 2. Event listeners handle key presses to update the state of movement keys. -->
        <!-- 3. The game loop updates the player's position based on the current key states and draws the player. -->
        <!-- 4. Boundary checks prevent the player from moving off-screen. -->
        <!-- 5. Optional animation shows an indicator on the side the player is facing. -->
    </section>
</body>
</html>
```

### Explanation:

1. **Player Object**: Contains properties for position, size, speed, velocity, and state (e.g., jumping).
2. **Keys Object**: Tracks the state of movement keys.
3. **Event Listeners**: Handle `keydown` and `keyup` events to update the state of movement keys.
4. **Game Loop**:
   - Updates the player's position based on the current key states.
   - Applies acceleration and deceleration logic.
   - Handles jumping physics.
   - Performs boundary checks.
   - Draws the player on the canvas.
5. **Optional Animation**: Displays an indicator on the side the player is facing.

This implementation ensures smooth movement, accurate boundary checks, and clear code structure.
 <!-- 114.63s -->
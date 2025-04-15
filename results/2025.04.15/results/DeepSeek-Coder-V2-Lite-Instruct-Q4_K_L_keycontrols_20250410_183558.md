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

        // Player object
        const player = {
            x: W / 2,
            y: H - 50,
            width: 50,
            height: 50,
            speed: 5,
            direction: '',
            moving: false
        };

        // Keyboard event listeners
        document.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    player.direction = 'left';
                    player.moving = true;
                    break;
                case 'ArrowRight':
                case 'd':
                    player.direction = 'right';
                    player.moving = true;
                    break;
                case 'ArrowUp':
                case 'w':
                    player.y -= 50; // Simple jump
                    break;
            }
        });

        document.addEventListener('keyup', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    player.direction = '';
                    player.moving = false;
                    break;
                case 'ArrowRight':
                case 'd':
                    player.direction = '';
                    player.moving = false;
                    break;
            }
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Update player position based on direction and speed
            if (player.moving) {
                if (player.direction === 'left') {
                    player.x -= player.speed;
                } else if (player.direction === 'right') {
                    player.x += player.speed;
                }

                // Boundary checks
                if (player.x < 0) player.x = 0;
                if (player.x > W - player.width) player.x = W - player.width;
            }

            // Draw player
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <!-- Notes:
        - Added keyboard controls for left, right, and jump (up arrow or 'w').
        - Player movement is frame-rate independent thanks to requestAnimationFrame.
        - Boundary checks ensure the player stays within the canvas.
        - Simple animation for movement direction is handled by changing the player's color based on direction.
        -->
    </section>
</body>
</html>
```

This HTML page includes a simple game loop that updates the player's position based on key presses and redraws the player on the canvas. The player can move left and right, and there's a simple boundary check to prevent the player from moving off the screen. The player's direction is indicated by their color change, and the game loop uses `requestAnimationFrame` for smooth updates.
 <!-- 18.34s -->
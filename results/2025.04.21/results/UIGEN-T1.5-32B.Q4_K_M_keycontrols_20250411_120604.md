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
            dx: 0,
            dy: 0,
            jumpStrength: 20,
            gravity: 1,
            grounded: true,
            facingRight: true,
            keysPressed: {
                left: false,
                right: false,
                up: false
            }
        };

        function drawPlayer() {
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);
            if (!player.grounded) {
                ctx.fillStyle = 'red';
                ctx.beginPath();
                ctx.arc(player.x + player.width / 2, player.y + player.height, player.height / 4, 0, Math.PI * 2);
                ctx.fill();
            }
            if (player.facingRight) {
                ctx.fillStyle = 'green';
                ctx.beginPath();
                ctx.arc(player.x + player.width, player.y + player.height / 2, player.height / 8, 0, Math.PI * 2);
                ctx.fill();
            } else {
                ctx.fillStyle = 'green';
                ctx.beginPath();
                ctx.arc(player.x, player.y + player.height / 2, player.height / 8, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function updatePlayer() {
            // Horizontal movement
            if (player.keysPressed.right) {
                player.dx = player.speed;
                player.facingRight = true;
            } else if (player.keysPressed.left) {
                player.dx = -player.speed;
                player.facingRight = false;
            } else {
                player.dx = 0;
            }

            // Vertical movement (jump)
            if (player.keysPressed.up && player.grounded) {
                player.dy = -player.jumpStrength;
                player.grounded = false;
            }

            // Gravity
            player.dy += player.gravity;

            // Update position
            player.x += player.dx;
            player.y += player.dy;

            // Boundary checks
            if (player.x < 0) player.x = 0;
            if (player.x + player.width > W) player.x = W - player.width;
            if (player.y + player.height > H) {
                player.y = H - player.height;
                player.dy = 0;
                player.grounded = true;
            }
        }

        function gameLoop(timestamp) {
            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update game state
            updatePlayer();

            // Draw game objects
            drawPlayer();

            // Request next frame
            requestAnimationFrame(gameLoop);
        }

        // Event listeners for key presses
        document.addEventListener('keydown', function(e) {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    player.keysPressed.left = true;
                    break;
                case 'ArrowRight':
                case 'd':
                    player.keysPressed.right = true;
                    break;
                case 'ArrowUp':
                case 'w':
                case ' ':
                    player.keysPressed.up = true;
                    break;
            }
        });

        document.addEventListener('keyup', function(e) {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    player.keysPressed.left = false;
                    break;
                case 'ArrowRight':
                case 'd':
                    player.keysPressed.right = false;
                    break;
                case 'ArrowUp':
                case 'w':
                case ' ':
                    player.keysPressed.up = false;
                    break;
            }
        });

        // Start the game loop
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <p>Notes:</p>
        <ul>
            <li>Player object handles position, size, speed, and movement state.</li>
            <li>Key event listeners update player keysPressed object.</li>
            <li>Game loop updates player position and draws player on canvas.</li>
            <li>Boundary checks ensure player stays within canvas.</li>
            <li>Basic sprite animation with facing direction indicator.</li>
        </ul>
    </section>
</body>
</html>
```
 <!-- 103.94s -->
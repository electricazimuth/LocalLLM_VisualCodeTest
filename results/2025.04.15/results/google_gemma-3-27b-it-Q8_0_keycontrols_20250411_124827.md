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

        // --- YOUR CODE GOES HERE ---

        const player = {
            x: 50,
            y: H - 50,
            width: 30,
            height: 50,
            speed: 0,
            maxSpeed: 5,
            acceleration: 0.2,
            deceleration: 0.1,
            isJumping: false,
            gravity: 0.5,
            verticalVelocity: 0
        };

        const keys = {};

        document.addEventListener('keydown', (e) => {
            keys[e.key] = true;
        });

        document.addEventListener('keyup', (e) => {
            keys[e.key] = false;
        });

        function gameLoop(timestamp) {
            // Clear canvas (usually needed)
            ctx.clearRect(0, 0, W, H);

            // --- Update logic ---
            handleMovement();
            handleJump();

            // --- Draw logic ---
            drawPlayer();

            requestAnimationFrame(gameLoop);
        }

        function handleMovement() {
            let horizontalMovement = 0;

            if (keys['ArrowLeft'] || keys['a']) {
                horizontalMovement -= 1;
            }
            if (keys['ArrowRight'] || keys['d']) {
                horizontalMovement += 1;
            }

            if (horizontalMovement !== 0) {
                player.speed += horizontalMovement * player.acceleration;
                player.speed = Math.max(-player.maxSpeed, Math.min(player.speed, player.maxSpeed));
            } else {
                // Decelerate
                if (player.speed > 0) {
                    player.speed -= player.deceleration;
                    if (player.speed < 0) player.speed = 0;
                } else if (player.speed < 0) {
                    player.speed += player.deceleration;
                    if (player.speed > 0) player.speed = 0;
                }
            }

            player.x += player.speed;

            // Boundary checks
            if (player.x < 0) {
                player.x = 0;
                player.speed = 0;
            } else if (player.x + player.width > W) {
                player.x = W - player.width;
                player.speed = 0;
            }
        }

        function handleJump() {
            if (player.isJumping) {
                player.verticalVelocity += player.gravity;
                player.y += player.verticalVelocity;

                if (player.y >= H - player.height) {
                    player.y = H - player.height;
                    player.isJumping = false;
                    player.verticalVelocity = 0;
                }
            }

            if (keys['Space'] && !player.isJumping) {
                player.isJumping = true;
                player.verticalVelocity = -10; // Initial jump velocity
            }
        }

        function drawPlayer() {
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <p>Key Controls:</p>
        <ul>
            <li>ArrowLeft/A: Move Left</li>
            <li>ArrowRight/D: Move Right</li>
            <li>Space: Jump</li>
        </ul>
        <p>Movement features acceleration/deceleration and handles multiple key presses.</p>
    </section>
</body>
</html>
```
 <!-- 111.61s -->
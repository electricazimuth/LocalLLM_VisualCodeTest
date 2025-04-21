```html
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

        let particles = [];
        let lastTime = 0;

        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 5;
                this.vy = (Math.random() - 0.5) * 5;
                this.lifespan = Math.random() * 200 + 50;
                this.color = `rgba(0, 0, 0, ${this.lifespan / 300})`;
                this.size = Math.random() * 2 + 1;
                this.age = 0;
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.age += dt;
            }

            draw() {
                const alpha = 1 - (this.age / this.lifespan);
                ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function spawnParticles(x, y) {
            for (let i = 0; i < 15; i++) {
                particles.push(new Particle(x, y));
            }
        }

        function gameLoop(timestamp) {
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            ctx.clearRect(0, 0, W, H);

            particles.forEach(particle => {
                particle.update(dt);
                particle.draw();
            });

            particles = particles.filter(particle => particle.age < particle.lifespan);

            requestAnimationFrame(gameLoop);
        }

        canvas.addEventListener('mousedown', (event) => {
            const rect = canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            spawnParticles(x, y);

            canvas.addEventListener('mousemove', moveHandler);

            function moveHandler(event) {
                const rect = canvas.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                spawnParticles(x, y);
            }

            canvas.addEventListener('mouseup', () => {
                canvas.removeEventListener('mousemove', moveHandler);
            }, { once: true });
        });

        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <p>Simple particle emitter created using JavaScript and HTML5 Canvas. Particles spawn on mouse click and move outwards with random velocities, fading and disappearing over time. Optimized for performance and smooth animation.</p>
    </section>
</body>
</html>
```
 <!-- 71.03s -->
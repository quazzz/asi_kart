<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Super Kart Racing — Lava Edition</title>
    <style>
        body {
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f0f, #1b1b1b);
            color: #f0f0f0;
            line-height: 1.6;
        }

        header {
            background: linear-gradient(90deg, #b00000, #ff5500);
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 3em;
            margin: 0;
            letter-spacing: 2px;
        }

        header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        section {
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;
        }

        h2 {
            color: #ff8800;
            border-bottom: 2px solid #333;
            padding-bottom: 5px;
        }

        .card {
            background: #1f1f1f;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }

        ul {
            padding-left: 20px;
        }

        li {
            margin: 6px 0;
        }

        code {
            background: #111;
            padding: 4px 8px;
            border-radius: 6px;
            color: #00ff99;
        }

        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }

        footer {
            text-align: center;
            padding: 30px;
            color: #aaa;
            font-size: 0.9em;
        }

        .highlight {
            color: #ffd700;
            font-weight: bold;
        }
    </style>
</head>
<body>

<header>
    <h1>SUPER KART RACING</h1>
    <p>Lava Edition 🔥 — Arcade Top-Down Racing</p>
</header>

<section>
    <div class="card">
        <h2>🏎️ About the Game</h2>
        <p>
            <strong>Super Kart Racing — Lava Edition</strong> is a fast-paced top-down
            kart racing game built with <span class="highlight">Python</span> and
            <span class="highlight">Pygame</span>.
        </p>
        <p>
            Race against AI opponents, survive lava hazards, master corners,
            and fight for <strong>1st place</strong> across multiple laps.
        </p>
    </div>

    <div class="card">
        <h2>✨ Features</h2>
        <ul>
            <li>Player vs AI kart racing</li>
            <li>Smooth arcade driving physics</li>
            <li>Grass slowdown & off-road penalties</li>
            <li>Lava & water hazards with respawn system</li>
            <li>Lap counting, checkpoints, and race positions</li>
            <li>Live results overlay after finishing</li>
        </ul>
    </div>

    <div class="card">
        <h2>🛠 Requirements</h2>
        <ul>
            <li>Python 3.8 or newer</li>
            <li>Pygame</li>
        </ul>
        <p>Install Pygame:</p>
        <code>pip install pygame</code>
    </div>

    <div class="card">
        <h2>▶️ How to Run</h2>
        <ol>
            <li>Save the game code as <code>main.py</code></li>
            <li>Open a terminal in the project folder</li>
            <li>Run:</li>
        </ol>
        <code>python main.py</code>
    </div>

    <div class="card">
        <h2>🎮 Controls</h2>
        <div class="controls-grid">
            <div>
                <h3>Menu</h3>
                <ul>
                    <li><code>SPACE</code> — Start race</li>
                </ul>
            </div>
            <div>
                <h3>Driving</h3>
                <ul>
                    <li><code>W / ↑</code> — Accelerate</li>
                    <li><code>S / ↓</code> — Brake / Reverse</li>
                    <li><code>A / ←</code> — Turn left</li>
                    <li><code>D / →</code> — Turn right</li>
                </ul>
            </div>
            <div>
                <h3>Race</h3>
                <ul>
                    <li><code>R</code> — Restart race</li>
                    <li><code>SPACE</code> — Restart after finishing</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>🏁 Gameplay Rules</h2>
        <ul>
            <li>Complete <strong>3 laps</strong> to finish the race</li>
            <li>Grass heavily reduces speed</li>
            <li>Lava & water cause instant respawn</li>
            <li>Respawn sends you to the last checkpoint</li>
            <li>Finishing order is based on total race time</li>
        </ul>
    </div>
</section>

<footer>
    Built with ❤️ using Python & Pygame<br>
    Super Kart Racing — Lava Edition
</footer>

</body>
</html>

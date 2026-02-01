<h1 align="center">🏎️ Super Kart Racing — Lava Edition</h1>

<p align="center">
  <strong>Arcade top-down kart racing game built with Python &amp; Pygame</strong><br>
  <em>Race fast. Dodge lava. Win.</em>
</p>

<hr>

<h2>✨ Features</h2>
<ul>
  <li>Player vs AI kart racing</li>
  <li>Lava 🔥 and water 💧 hazards</li>
  <li>Grass slowdown &amp; off-road penalties</li>
  <li>Checkpoints, laps, positions &amp; finish times</li>
  <li>Results overlay after finishing</li>
</ul>

<hr>

<h2>🛠 Requirements</h2>
<ul>
  <li>Python 3.8 or newer</li>
  <li>Pygame</li>
</ul>

<p>Install Pygame:</p>

<pre><code>pip install pygame</code></pre>

<hr>

<h2>▶️ How to Run</h2>
<ol>
  <li>Save the game code as <code>main.py</code></li>
  <li>Open a terminal in the project folder</li>
  <li>Run the game:</li>
</ol>

<pre><code>python main.py</code></pre>

<hr>

<h2>🎮 Controls</h2>

<table>
  <tr>
    <th align="left">Action</th>
    <th align="left">Key</th>
  </tr>
  <tr>
    <td>Accelerate</td>
    <td>W / ↑</td>
  </tr>
  <tr>
    <td>Brake / Reverse</td>
    <td>S / ↓</td>
  </tr>
  <tr>
    <td>Turn Left</td>
    <td>A / ←</td>
  </tr>
  <tr>
    <td>Turn Right</td>
    <td>D / →</td>
  </tr>
  <tr>
    <td>Start Race</td>
    <td>SPACE</td>
  </tr>
  <tr>
    <td>Restart Race</td>
    <td>R</td>
  </tr>
  <tr>
    <td>Restart After Finish</td>
    <td>SPACE</td>
  </tr>
</table>

<hr>

<h2>🏁 Gameplay</h2>
<ul>
  <li>Complete <strong>3 laps</strong> to finish the race</li>
  <li>Driving on grass heavily reduces speed</li>
  <li>Touching lava or water causes instant respawn</li>
  <li>Respawn places you at the last checkpoint</li>
  <li>Finish order is determined by total race time</li>
</ul>

<hr>

<h2>📦 Build Windows EXE</h2>

<p>Install PyInstaller:</p>
<pre><code>pip install pyinstaller</code></pre>

<p>Build the executable:</p>
<pre><code>pyinstaller --onefile --windowed main.py</code></pre>

<p>The final executable will be located in:</p>
<pre><code>dist/main.exe</code></pre>

<hr>

<h2>🚀 Tips</h2>
<ul>
  <li>Slow down before sharp turns for better control</li>
  <li>Watch AI racing lines to find faster paths</li>
  <li>Lava hazards are placed on the racing line — stay alert</li>
</ul>

<hr>

<p align="center">
  Built with ❤️ using Python &amp; Pygame<br>
  <strong>Super Kart Racing — Lava Edition</strong>
</p>

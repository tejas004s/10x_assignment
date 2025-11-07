const canvas = document.getElementById("wallCanvas");
const ctx = canvas.getContext("2d");

const scaleX = 80;
const scaleY = 80;

document.getElementById("configForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const width = parseFloat(document.getElementById("wallWidth").value);
  const height = parseFloat(document.getElementById("wallHeight").value);
  const coverageWidth = parseFloat(document.getElementById("coverageWidth").value);
  const obstacles = getObstaclesFromEditor();

  if (isNaN(width) || isNaN(height) || isNaN(coverageWidth)) {
    alert("Please enter valid wall and coverage dimensions.");
    return;
  }

  if (obstacles.length === 0 && !confirm("No obstacles added. Simulate anyway?")) return;

  const config = { width, height, coverage_width: coverageWidth, obstacles };
  console.log("✅ Posting config:", JSON.stringify(config, null, 2));

  try {
    const response = await fetch("http://localhost:8000/api/trajectories", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config)
    });

    if (!response.ok) throw new Error("Backend error");

    const waypoints = await response.json();
    drawWall(width, height);
    drawObstacles(obstacles);
    animatePath(waypoints, obstacles);

    const pathLength = waypoints.reduce((sum, wp, i) => {
      if (i === 0) return sum;
      const dx = wp.x - waypoints[i - 1].x;
      const dy = wp.y - waypoints[i - 1].y;
      return sum + Math.sqrt(dx * dx + dy * dy);
    }, 0);

    const coveragePercent = ((pathLength * coverageWidth) / (width * height)) * 100;
    const duration = waypoints.length * 0.1;

    document.getElementById("metricsDisplay").innerHTML = `
      <h3>Metrics</h3>
      <p>Path Length: ${pathLength.toFixed(2)} m</p>
      <p>Coverage: ${coveragePercent.toFixed(2)}%</p>
      <p>Estimated Duration: ${duration.toFixed(2)} s</p>
    `;
  } catch (err) {
    alert("Failed to fetch trajectory. Check backend and inputs.");
  }
});

function drawWall(width, height) {
  canvas.width = width * scaleX;
  canvas.height = height * scaleY;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#000000";
  ctx.strokeRect(0, 0, canvas.width, canvas.height);
}

function addObstacle(x = 0, y = 0, w = 1, h = 1) {
  const container = document.getElementById("obstacleList");

  const div = document.createElement("div");
  div.className = "obstacle-card";

  const xInput = document.createElement("input");
  xInput.type = "number";
  xInput.step = "0.1";
  xInput.value = x;

  const yInput = document.createElement("input");
  yInput.type = "number";
  yInput.step = "0.1";
  yInput.value = y;

  const wInput = document.createElement("input");
  wInput.type = "number";
  wInput.step = "0.1";
  wInput.value = w;

  const hInput = document.createElement("input");
  hInput.type = "number";
  hInput.step = "0.1";
  hInput.value = h;

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.textContent = "Remove";
  removeBtn.className = "remove-btn";
  removeBtn.onclick = () => div.remove();

  div.appendChild(labelWrap("X:", xInput));
  div.appendChild(labelWrap("Y:", yInput));
  div.appendChild(labelWrap("Width:", wInput));
  div.appendChild(labelWrap("Height:", hInput));
  div.appendChild(removeBtn);

  container.appendChild(div);
}

function labelWrap(text, input) {
  const label = document.createElement("label");
  label.textContent = text;
  label.appendChild(input);
  return label;
}

function getObstaclesFromEditor() {
  const cards = document.querySelectorAll(".obstacle-card");
  const obstacles = [];

  cards.forEach((card, index) => {
    const inputs = card.querySelectorAll("input");
    if (inputs.length !== 4) {
      console.warn(`Obstacle ${index} missing inputs`);
      return;
    }

    const x = parseFloat(inputs[0].value);
    const y = parseFloat(inputs[1].value);
    const w = parseFloat(inputs[2].value);
    const h = parseFloat(inputs[3].value);

    if ([x, y, w, h].some(v => isNaN(v) || v < 0)) {
      console.warn(`Obstacle ${index} has invalid values`);
      return;
    }

    obstacles.push({ x, y, width: w, height: h });
  });

  return obstacles;
}

function previewObstacles() {
  const width = parseFloat(document.getElementById("wallWidth").value);
  const height = parseFloat(document.getElementById("wallHeight").value);
  const obstacles = getObstaclesFromEditor();

  drawWall(width, height);
  drawObstacles(obstacles);
}

function drawObstacles(obstacles) {
  ctx.fillStyle = "#ff4d4d";
  obstacles.forEach(obs => {
    ctx.fillRect(
      obs.x * scaleX,
      canvas.height - (obs.y + obs.height) * scaleY,
      obs.width * scaleX,
      obs.height * scaleY
    );
  });
}

function isInsideObstacle(x, y, obstacles) {
  return obstacles.some(obs =>
    x >= obs.x &&
    x <= obs.x + obs.width &&
    y >= obs.y &&
    y <= obs.y + obs.height
  );
}

function animatePath(waypoints, obstacles) {
  let i = 1;
  ctx.strokeStyle = "blue";
  ctx.lineWidth = 2;

  function step() {
    if (i >= waypoints.length) return;

    const prev = waypoints[i - 1];
    const curr = waypoints[i];

    const x1 = prev.x * scaleX;
    const y1 = canvas.height - prev.y * scaleY;
    const x2 = curr.x * scaleX;
    const y2 = canvas.height - curr.y * scaleY;

    const prevInside = isInsideObstacle(prev.x, prev.y, obstacles);
    const currInside = isInsideObstacle(curr.x, curr.y, obstacles);

    if (!prevInside && !currInside) {
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    if (!currInside) {
      drawRobot(x2, y2);
    }

    i++;
    setTimeout(step, 100);
  }

  step();
}

function drawRobot(x, y) {
  ctx.fillStyle = "#00cc66";
  ctx.beginPath();
  ctx.arc(x, y, 5, 0, 2 * Math.PI);
  ctx.fill();
}

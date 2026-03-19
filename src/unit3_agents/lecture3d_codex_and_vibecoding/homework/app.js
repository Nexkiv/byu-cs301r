const CUBE_TEMPLATES = {
  green: ["5", "4", "x", "-", "6", "^"] ,
  red: ["0", "2", "+", "3", "-", "1"],
  blue: ["0", "2", "÷", "x", "3", "1"],
  black: ["7", "÷", "√", "8", "9", "+"],
};

const COLORS = ["red", "blue", "green", "black"];

const ZONES = ["resources", "goal", "required", "permitted", "forbidden"];

const state = {
  players: [],
  currentPlayerIndex: 0,
  goalSetterIndex: 0,
  phase: "idle",
  cubes: [],
  goalLocked: false,
  moveMade: false,
  lastMoverIndex: null,
  challenge: null,
  goalValue: null,
  goalOrder: [],
};

const els = {
  playerCount: document.getElementById("playerCount"),
  playerNames: document.getElementById("playerNames"),
  startMatchBtn: document.getElementById("startMatchBtn"),
  newShakeBtn: document.getElementById("newShakeBtn"),
  lockGoalBtn: document.getElementById("lockGoalBtn"),
  endTurnBtn: document.getElementById("endTurnBtn"),
  challengeNowBtn: document.getElementById("challengeNowBtn"),
  challengeNeverBtn: document.getElementById("challengeNeverBtn"),
  resolveChallengeBtn: document.getElementById("resolveChallengeBtn"),
  nextRoundBtn: document.getElementById("nextRoundBtn"),
  playersList: document.getElementById("playersList"),
  resourcesZone: document.getElementById("resourcesZone"),
  goalZone: document.getElementById("goalZone"),
  requiredZone: document.getElementById("requiredZone"),
  permittedZone: document.getElementById("permittedZone"),
  forbiddenZone: document.getElementById("forbiddenZone"),
  phaseLabel: document.getElementById("phaseLabel"),
  goalSetterLabel: document.getElementById("goalSetterLabel"),
  turnLabel: document.getElementById("turnLabel"),
  historyLog: document.getElementById("historyLog"),
  challengeInfo: document.getElementById("challengeInfo"),
  challengerInput: document.getElementById("challengerInput"),
  moverInput: document.getElementById("moverInput"),
  thirdInput: document.getElementById("thirdInput"),
  submitSolutionsBtn: document.getElementById("submitSolutionsBtn"),
  validationMsg: document.getElementById("validationMsg"),
};

function initPlayerInputs() {
  els.playerNames.innerHTML = "";
  const count = Number(els.playerCount.value);
  for (let i = 0; i < count; i++) {
    const input = document.createElement("input");
    input.placeholder = `Player ${i + 1}`;
    input.value = `Player ${i + 1}`;
    input.dataset.index = i;
    els.playerNames.appendChild(input);
  }
}

function createCubes() {
  const cubes = [];
  let idCounter = 1;
  COLORS.forEach((color) => {
    for (let i = 0; i < 6; i++) {
      const faces = CUBE_TEMPLATES[color];
      cubes.push({
        id: `cube-${idCounter++}`,
        color,
        faces,
        currentFace: faces[0],
        zone: "resources",
      });
    }
  });
  return cubes;
}

function rollCubes() {
  state.cubes.forEach((cube) => {
    const face = cube.faces[Math.floor(Math.random() * cube.faces.length)];
    cube.currentFace = face;
    cube.zone = "resources";
  });
  state.goalLocked = false;
  state.moveMade = false;
  state.lastMoverIndex = null;
  state.challenge = null;
  state.goalValue = null;
  state.goalOrder = [];
  clearChallengeInputs();
  renderAll();
  logHistory("New shake: cubes rolled.");
}

function renderAll() {
  renderPlayers();
  renderZones();
  updateLabels();
  updateButtons();
}

function renderPlayers() {
  els.playersList.innerHTML = "";
  state.players.forEach((player, index) => {
    const card = document.createElement("div");
    card.className = "player-card" + (index === state.currentPlayerIndex ? " active" : "");
    const name = document.createElement("div");
    name.className = "player-name";
    name.textContent = player.name;
    const score = document.createElement("div");
    score.className = "player-score";
    score.textContent = `${player.score} pts`;
    card.appendChild(name);
    card.appendChild(score);
    els.playersList.appendChild(card);
  });
}

function renderZones() {
  ZONES.forEach((zoneName) => {
    const zoneEl = getZoneEl(zoneName);
    zoneEl.innerHTML = "";
    if (zoneName === "goal") {
      state.goalOrder.forEach((id) => {
        const cube = state.cubes.find((c) => c.id === id);
        if (!cube) return;
        const el = createCubeElement(cube);
        zoneEl.appendChild(el);
      });
      return;
    }
    const cubes = state.cubes.filter((c) => c.zone === zoneName);
    cubes.forEach((cube) => {
      const el = createCubeElement(cube);
      zoneEl.appendChild(el);
    });
  });
}

function createCubeElement(cube) {
  const el = document.createElement("div");
  el.className = `cube ${cube.color}`;
  el.textContent = cube.currentFace;
  el.draggable = true;
  el.dataset.id = cube.id;
  el.addEventListener("dragstart", onDragStart);
  el.addEventListener("dragover", (e) => {
    if (cube.zone === "goal" && state.phase === "set_goal" && !state.goalLocked) {
      e.preventDefault();
    }
  });
  return el;
}

function removeCubeElement(id) {
  const el = document.querySelector(`.cube[data-id="${id}"]`);
  if (el && el.parentElement) {
    el.parentElement.removeChild(el);
  }
}

function getZoneEl(zone) {
  switch (zone) {
    case "resources": return els.resourcesZone;
    case "goal": return els.goalZone;
    case "required": return els.requiredZone;
    case "permitted": return els.permittedZone;
    case "forbidden": return els.forbiddenZone;
    default: return null;
  }
}

function onDragStart(e) {
  const id = e.currentTarget.dataset.id;
  e.dataTransfer.setData("text/plain", id);
}

function attachZoneDnD(zoneEl, zoneName) {
  zoneEl.addEventListener("dragover", (e) => {
    if (canDropInto(zoneName)) {
      e.preventDefault();
    }
  });
  zoneEl.addEventListener("drop", (e) => {
    e.preventDefault();
    const id = e.dataTransfer.getData("text/plain");
    const cube = state.cubes.find((c) => c.id === id);
    if (!cube) return;
    if (!canDropInto(zoneName, cube)) return;

    if (zoneName === "goal" && state.phase === "set_goal") {
      const target = e.target.closest(".cube");
      const targetId = target?.dataset?.id;
      cube.zone = "goal";
      if (!state.goalOrder.includes(cube.id)) {
        if (targetId && state.goalOrder.includes(targetId)) {
          const idx = state.goalOrder.indexOf(targetId);
          state.goalOrder.splice(idx, 0, cube.id);
        } else {
          state.goalOrder.push(cube.id);
        }
      }
      renderZones();
      updateButtons();
      return;
    }

    if (zoneName === "resources" && cube.zone === "goal" && state.phase === "set_goal") {
      cube.zone = "resources";
      state.goalOrder = state.goalOrder.filter((cid) => cid !== cube.id);
      renderZones();
      updateButtons();
      return;
    }

    cube.zone = zoneName;
    if (zoneName !== "goal" && cube.zone !== "goal") {
      state.moveMade = zoneName !== "resources" && state.phase === "move";
      state.lastMoverIndex = state.currentPlayerIndex;
    }
    renderZones();
    updateButtons();
  });
}

function canDropInto(zoneName, cube) {
  if (!cube) return true;
  if (state.phase === "set_goal") {
    if (zoneName === "goal") {
      if (cube.zone !== "resources") return false;
      if (state.goalLocked) return false;
      if (els.goalZone.children.length >= 6) return false;
      return true;
    }
    if (zoneName === "resources" && cube.zone === "goal") {
      return true;
    }
    if (state.goalLocked) return false;
    return false;
  }
  if (state.phase === "move") {
    if (!["required", "permitted", "forbidden"].includes(zoneName)) return false;
    if (cube.zone !== "resources") return false;
    if (state.moveMade) return false;
    return true;
  }
  return false;
}

function updateLabels() {
  els.phaseLabel.textContent = phaseLabel(state.phase);
  els.goalSetterLabel.textContent = state.players[state.goalSetterIndex]?.name ?? "—";
  els.turnLabel.textContent = state.players[state.currentPlayerIndex]?.name ?? "—";
}

function phaseLabel(phase) {
  switch (phase) {
    case "idle": return "Not started";
    case "set_goal": return "Setting goal";
    case "move": return "R/P/F moves";
    case "challenge": return "Challenge in progress";
    case "resolved": return "Ready for next round";
    default: return phase;
  }
}

function updateButtons() {
  const inMatch = state.players.length > 0;
  els.newShakeBtn.disabled = !inMatch;
  els.lockGoalBtn.disabled = !(state.phase === "set_goal" && !state.goalLocked);
  els.endTurnBtn.disabled = !(state.phase === "move" && state.moveMade);
  els.challengeNowBtn.disabled = !(state.phase === "move");
  const lastCube = resourcesCount() === 1;
  els.challengeNeverBtn.disabled = !(state.phase === "move");
  if (state.phase === "move" && lastCube) {
    els.challengeNowBtn.disabled = true;
  }
  els.resolveChallengeBtn.disabled = !(state.phase === "challenge" && state.challenge?.solutionsSubmitted);
  els.nextRoundBtn.disabled = state.phase !== "resolved";
  els.submitSolutionsBtn.disabled = state.phase !== "challenge";
}

function resourcesCount() {
  return state.cubes.filter((c) => c.zone === "resources").length;
}

function lockGoal() {
  const goalCubes = state.cubes.filter((c) => c.zone === "goal");
  if (goalCubes.length === 0 || goalCubes.length > 6) {
    alert("Goal must use 1–6 cubes.");
    return;
  }
  const goalExpr = getGoalExpression();
  const evalResult = evaluateGoal(goalExpr);
  if (!evalResult.ok) {
    alert(`Goal invalid: ${evalResult.error}`);
    return;
  }
  state.goalValue = evalResult.value;
  state.goalLocked = true;
  state.phase = "move";
  state.currentPlayerIndex = nextPlayerIndex(state.goalSetterIndex);
  state.moveMade = false;
  logHistory(`Goal set to ${goalExpr} = ${state.goalValue}.`);
  renderAll();
}

function getGoalExpression() {
  const faces = Array.from(els.goalZone.querySelectorAll(".cube")).map((el) => el.textContent);
  return faces.join("");
}

function evaluateGoal(expr) {
  const tokens = tokenizeGoal(expr);
  if (!tokens.ok) return tokens;
  const rpn = toRpn(tokens.value);
  if (!rpn.ok) return rpn;
  const value = evalRpn(rpn.value);
  return value;
}

function tokenizeGoal(expr) {
  const raw = expr.replace(/\s+/g, "");
  if (raw.length === 0) return { ok: false, error: "Empty goal" };
  const tokens = [];
  let i = 0;
  while (i < raw.length) {
    const ch = raw[i];
    if (/\d/.test(ch)) {
      let num = ch;
      if (i + 1 < raw.length && /\d/.test(raw[i + 1])) {
        num += raw[i + 1];
        i++;
        if (i + 1 < raw.length && /\d/.test(raw[i + 1])) {
          return { ok: false, error: "Goal numbers may have at most two digits" };
        }
      }
      tokens.push({ type: "number", value: Number(num) });
      i++;
      continue;
    }
    if (isOperator(ch)) {
      tokens.push({ type: "op", value: ch });
      i++;
      continue;
    }
    return { ok: false, error: `Invalid character '${ch}'` };
  }
  return { ok: true, value: normalizeRoot(tokens) };
}

function tokenizeSubmission(expr) {
  const raw = expr.replace(/\s+/g, "");
  if (raw.length === 0) return { ok: false, error: "Empty submission" };
  const tokens = [];
  let i = 0;
  while (i < raw.length) {
    const ch = raw[i];
    if (/\d/.test(ch)) {
      tokens.push({ type: "number", value: Number(ch) });
      i++;
      continue;
    }
    if (ch === "(" || ch === ")") {
      tokens.push({ type: "paren", value: ch });
      i++;
      continue;
    }
    if (isOperator(ch)) {
      tokens.push({ type: "op", value: ch });
      i++;
      continue;
    }
    return { ok: false, error: `Invalid character '${ch}'` };
  }
  return { ok: true, value: normalizeRoot(tokens) };
}

function isOperator(ch) {
  return ["+", "-", "x", "÷", "^", "√"].includes(ch);
}

function normalizeRoot(tokens) {
  const normalized = [];
  tokens.forEach((token, idx) => {
    if (token.type === "op" && token.value === "√") {
      const prev = normalized[normalized.length - 1];
      if (!prev || (prev.type === "op" && prev.value !== ")") || (prev.type === "paren" && prev.value === "(")) {
        normalized.push({ type: "number", value: 2 });
      }
      normalized.push({ type: "op", value: "√" });
      return;
    }
    normalized.push(token);
  });
  return normalized;
}

const PRECEDENCE = {
  "√": 4,
  "^": 4,
  "x": 3,
  "÷": 3,
  "+": 2,
  "-": 2,
};

const RIGHT_ASSOC = new Set(["^", "√"]);

function toRpn(tokens) {
  const output = [];
  const ops = [];
  let lastType = null;
  for (const token of tokens) {
    if (token.type === "number") {
      output.push(token);
      lastType = "number";
      continue;
    }
    if (token.type === "paren") {
      if (token.value === "(") {
        ops.push(token);
        lastType = "paren";
      } else {
        while (ops.length && ops[ops.length - 1].value !== "(") {
          output.push(ops.pop());
        }
        if (!ops.length) return { ok: false, error: "Mismatched parentheses" };
        ops.pop();
        lastType = "paren";
      }
      continue;
    }
    if (token.type === "op") {
      if (!lastType || lastType === "op") {
        return { ok: false, error: "Two operators in a row" };
      }
      while (ops.length) {
        const top = ops[ops.length - 1];
        if (top.type !== "op") break;
        if ((RIGHT_ASSOC.has(token.value) && PRECEDENCE[token.value] < PRECEDENCE[top.value]) ||
            (!RIGHT_ASSOC.has(token.value) && PRECEDENCE[token.value] <= PRECEDENCE[top.value])) {
          output.push(ops.pop());
        } else {
          break;
        }
      }
      ops.push(token);
      lastType = "op";
    }
  }
  while (ops.length) {
    const op = ops.pop();
    if (op.type === "paren") return { ok: false, error: "Mismatched parentheses" };
    output.push(op);
  }
  return { ok: true, value: output };
}

function evalRpn(rpn) {
  const stack = [];
  for (const token of rpn) {
    if (token.type === "number") {
      stack.push(token.value);
      continue;
    }
    const b = stack.pop();
    const a = stack.pop();
    if (a === undefined || b === undefined) return { ok: false, error: "Invalid expression" };
    let result;
    switch (token.value) {
      case "+": result = a + b; break;
      case "-": result = a - b; break;
      case "x": result = a * b; break;
      case "÷": result = b === 0 ? NaN : a / b; break;
      case "^": result = Math.pow(a, b); break;
      case "√": result = a === 0 ? NaN : Math.pow(b, 1 / a); break;
      default: return { ok: false, error: "Unknown operator" };
    }
    if (!Number.isFinite(result)) return { ok: false, error: "Invalid arithmetic" };
    stack.push(result);
  }
  if (stack.length !== 1) return { ok: false, error: "Invalid expression" };
  return { ok: true, value: stack[0] };
}

function startMatch() {
  const inputs = Array.from(els.playerNames.querySelectorAll("input"));
  state.players = inputs.map((input) => ({ name: input.value.trim() || "Player", score: 0 }));
  state.goalSetterIndex = 0;
  state.currentPlayerIndex = 0;
  state.phase = "set_goal";
  state.cubes = createCubes();
  rollCubes();
  logHistory("Match started.");
  renderAll();
}

function nextPlayerIndex(idx) {
  return (idx + 1) % state.players.length;
}

function endTurn() {
  if (!state.moveMade) return;
  state.moveMade = false;
  state.currentPlayerIndex = nextPlayerIndex(state.currentPlayerIndex);
  logHistory(`${state.players[state.currentPlayerIndex].name}'s turn.`);
  renderAll();
}

function startChallenge(type) {
  if (state.phase !== "move") return;
  state.phase = "challenge";
  state.challenge = {
    type,
    challengerIndex: state.currentPlayerIndex,
    moverIndex: state.lastMoverIndex ?? state.goalSetterIndex,
    thirdIndex: state.players.length === 3 ? state.players.findIndex((_, i) => i !== state.currentPlayerIndex && i !== (state.lastMoverIndex ?? state.goalSetterIndex)) : null,
    solutionsSubmitted: false,
  };
  clearChallengeInputs();
  els.challengeInfo.textContent = `${state.players[state.challenge.challengerIndex].name} challenges ${type}.`;
  logHistory(`Challenge ${type} issued by ${state.players[state.challenge.challengerIndex].name}.`);
  renderAll();
}

function clearChallengeInputs() {
  els.challengerInput.value = "";
  els.moverInput.value = "";
  els.thirdInput.value = "";
  els.validationMsg.textContent = "";
}

function submitSolutions() {
  const challenge = state.challenge;
  if (!challenge) return;

  const submissions = {
    challenger: els.challengerInput.value.trim(),
    mover: els.moverInput.value.trim(),
    third: els.thirdInput.value.trim(),
  };

  const validation = validateSubmissions(submissions, challenge.type);
  if (!validation.ok) {
    els.validationMsg.textContent = validation.error;
    return;
  }
  els.validationMsg.textContent = "Submissions validated.";
  challenge.submissions = validation.results;
  challenge.solutionsSubmitted = true;
  renderAll();
}

function validateSubmissions(submissions, challengeType) {
  const results = {};
  const goalValue = state.goalValue;
  if (goalValue === null) return { ok: false, error: "Goal not set" };

  const roles = ["challenger", "mover", "third"];
  for (const role of roles) {
    const expr = submissions[role];
    if (!expr) {
      results[role] = { ok: false, reason: "No submission" };
      continue;
    }
    const parsed = tokenizeSubmission(expr);
    if (!parsed.ok) return { ok: false, error: `${role}: ${parsed.error}` };
    if (parsed.value.filter((t) => t.type === "number" || t.type === "op").length < 2) {
      return { ok: false, error: `${role}: Must use at least two cubes` };
    }
    const rpn = toRpn(parsed.value);
    if (!rpn.ok) return { ok: false, error: `${role}: ${rpn.error}` };
    const value = evalRpn(rpn.value);
    if (!value.ok) return { ok: false, error: `${role}: ${value.error}` };

    const equal = Math.abs(value.value - goalValue) < 1e-9;
    if (!equal) {
      results[role] = { ok: false, reason: "Does not equal goal" };
      continue;
    }

    const usage = validateCubeUsage(parsed.value, challengeType);
    if (!usage.ok) return { ok: false, error: `${role}: ${usage.error}` };
    results[role] = { ok: true, value: value.value, used: usage.usedFaces };
  }

  return { ok: true, results };
}

function validateCubeUsage(tokens, challengeType) {
  const faceUsage = {};
  tokens.forEach((token) => {
    if (token.type === "number") {
      const key = String(token.value);
      faceUsage[key] = (faceUsage[key] || 0) + 1;
    } else if (token.type === "op") {
      const key = token.value;
      faceUsage[key] = (faceUsage[key] || 0) + 1;
    }
  });

  const requiredFaces = countFaces("required");
  const permittedFaces = countFaces("permitted");
  const resourceFaces = countFaces("resources");
  const totalRequired = sumCounts(requiredFaces);

  for (const [face, count] of Object.entries(requiredFaces)) {
    if ((faceUsage[face] || 0) < count) {
      return { ok: false, error: `Missing required cube face '${face}'` };
    }
  }

  for (const [face, count] of Object.entries(faceUsage)) {
    const available = (requiredFaces[face] || 0) + (permittedFaces[face] || 0) + (resourceFaces[face] || 0);
    if (count > available) {
      return { ok: false, error: `Not enough cubes for face '${face}'` };
    }
  }

  const usedTotal = sumCounts(faceUsage);
  const permittedTotal = sumCounts(permittedFaces);
  const resourcesTotal = sumCounts(resourceFaces);
  const minResourcesNeeded = Math.max(0, usedTotal - totalRequired - permittedTotal);

  if (challengeType === "Now" && minResourcesNeeded > 1) {
    return { ok: false, error: "Now challenge allows at most one Resource cube" };
  }

  if (minResourcesNeeded > resourcesTotal) {
    return { ok: false, error: "Uses more Resource cubes than available" };
  }

  return { ok: true, usedFaces: faceUsage };
}

function countFaces(zoneName) {
  const counts = {};
  state.cubes
    .filter((c) => c.zone === zoneName)
    .forEach((cube) => {
      const face = cube.currentFace;
      counts[face] = (counts[face] || 0) + 1;
    });
  return counts;
}

function sumCounts(counts) {
  return Object.values(counts).reduce((sum, count) => sum + count, 0);
}

function resolveChallenge() {
  const challenge = state.challenge;
  if (!challenge || !challenge.solutionsSubmitted) return;

  const roles = {
    challenger: challenge.challengerIndex,
    mover: challenge.moverIndex,
    third: challenge.thirdIndex,
  };

  const correctness = {
    challenger: challenge.submissions.challenger?.ok ?? false,
    mover: challenge.submissions.mover?.ok ?? false,
    third: challenge.submissions.third?.ok ?? false,
  };

  let challengerCorrect = false;
  if (challenge.type === "Now") {
    challengerCorrect = correctness.challenger;
  } else {
    challengerCorrect = !correctness.mover && !correctness.third;
  }

  const scores = { challenger: 0, mover: 0, third: 0 };

  if (challengerCorrect) {
    scores.challenger = 6;
    if (roles.mover !== null) scores.mover = 2;
    if (roles.third !== null) scores.third = 2;
  } else {
    scores.challenger = 2;
    if (correctness.mover) scores.mover = 6; else if (roles.mover !== null) scores.mover = 2;

    if (roles.third !== null) {
      if (correctness.third) {
        const sixPoint = challenge.type === "Never" || (challenge.type === "Now" && !correctness.challenger);
        scores.third = sixPoint ? 6 : 4;
      } else {
        scores.third = 2;
      }
    }
  }

  applyScore(roles.challenger, scores.challenger, "challenger");
  if (roles.mover !== null) applyScore(roles.mover, scores.mover, "mover");
  if (roles.third !== null) applyScore(roles.third, scores.third, "third party");

  state.phase = "resolved";
  logHistory(`Challenge ${challenge.type} resolved.`);
  renderAll();
}

function applyScore(index, points, roleLabel) {
  if (index === null || index === undefined) return;
  state.players[index].score += points;
  logHistory(`${state.players[index].name} (${roleLabel}) +${points} points.`);
}

function nextRound() {
  state.goalSetterIndex = nextPlayerIndex(state.goalSetterIndex);
  state.currentPlayerIndex = state.goalSetterIndex;
  state.phase = "set_goal";
  state.goalLocked = false;
  state.challenge = null;
  clearChallengeInputs();
  rollCubes();
  renderAll();
}

function logHistory(message) {
  const item = document.createElement("div");
  item.className = "history-item";
  const time = new Date().toLocaleTimeString();
  item.textContent = `[${time}] ${message}`;
  els.historyLog.prepend(item);
}

els.startMatchBtn.addEventListener("click", startMatch);
els.newShakeBtn.addEventListener("click", rollCubes);
els.lockGoalBtn.addEventListener("click", lockGoal);
els.endTurnBtn.addEventListener("click", endTurn);
els.challengeNowBtn.addEventListener("click", () => startChallenge("Now"));
els.challengeNeverBtn.addEventListener("click", () => startChallenge("Never"));
els.submitSolutionsBtn.addEventListener("click", submitSolutions);
els.resolveChallengeBtn.addEventListener("click", resolveChallenge);
els.nextRoundBtn.addEventListener("click", nextRound);
els.playerCount.addEventListener("change", initPlayerInputs);

[els.resourcesZone, els.goalZone, els.requiredZone, els.permittedZone, els.forbiddenZone].forEach((zoneEl) => {
  attachZoneDnD(zoneEl, zoneEl.dataset.zone);
});

initPlayerInputs();
renderAll();

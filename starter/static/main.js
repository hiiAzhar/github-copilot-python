// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudoku-top-10';
const THEME_KEY = 'sudoku-theme';
let puzzle = [];
let givens = [];
let locked = [];
let timerId = null;
let startedAt = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let gameCompleted = false;

function applyTheme(theme) {
  const darkMode = theme === 'dark';
  document.documentElement.dataset.theme = darkMode ? 'dark' : 'light';
  const toggle = document.getElementById('theme-toggle');
  toggle.textContent = darkMode ? 'Light mode' : 'Dark mode';
  toggle.setAttribute('aria-pressed', darkMode.toString());
}

function toggleTheme() {
  const currentTheme = document.documentElement.dataset.theme || 'light';
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  localStorage.setItem(THEME_KEY, nextTheme);
  applyTheme(nextTheme);
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainder = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainder}`;
}

function updateTimer() {
  if (startedAt === null) return;
  elapsedSeconds = Math.floor((Date.now() - startedAt) / 1000);
  document.getElementById('timer').textContent = `Time: ${formatTime(elapsedSeconds)}`;
}

function startTimer() {
  stopTimer();
  startedAt = Date.now();
  elapsedSeconds = 0;
  updateTimer();
  timerId = window.setInterval(updateTimer, 1000);
}

function stopTimer() {
  if (timerId !== null) {
    window.clearInterval(timerId);
    timerId = null;
  }
}

function readLeaderboard() {
  try {
    const scores = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
    return Array.isArray(scores) ? scores : [];
  } catch (error) {
    return [];
  }
}

function writeLeaderboard(scores) {
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
  } catch (error) {
    return;
  }
}

function renderLeaderboard() {
  const body = document.getElementById('leaderboard-body');
  body.innerHTML = '';
  readLeaderboard().forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatTime(score.time), score.difficulty, score.hints]
      .forEach((value) => {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      });
    body.appendChild(row);
  });
}

function recordCompletion() {
  if (gameCompleted) return;
  gameCompleted = true;
  stopTimer();
  const name = window.prompt('Enter your name for the Top 10 leaderboard:') || 'Anonymous';
  const difficulty = document.getElementById('difficulty').value;
  const scores = readLeaderboard();
  scores.push({
    name: name.trim().slice(0, 30) || 'Anonymous',
    time: elapsedSeconds,
    difficulty,
    hints: hintsUsed,
  });
  scores.sort((first, second) => first.time - second.time);
  writeLeaderboard(scores.slice(0, 10));
  renderLeaderboard();
}

function showCompletion(message) {
  message.textContent = 'Congratulations! You solved it!';
  message.className = 'success';
  recordCompletion();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.inputMode = 'numeric';
      input.setAttribute('role', 'gridcell');
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      const boxIsAlternate = (Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 1;
      input.className = boxIsAlternate
        ? 'sudoku-cell box-alt'
        : 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', async (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        e.target.classList.remove('incorrect', 'correct');
        e.target.removeAttribute('aria-invalid');
        if (val) {
          await submitMove(e.target);
        }
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, givenCells) {
  puzzle = puz;
  givens = givenCells;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (givens[i][j]) {
        inp.value = val;
        inp.disabled = true;
        inp.setAttribute('aria-readonly', 'true');
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.removeAttribute('aria-readonly');
      }
    }
  }
}

function setLockedCell(row, col, value) {
  const input = document.querySelector(
    `.sudoku-cell[data-row="${row}"][data-col="${col}"]`
  );
  if (!input) return;
  input.value = value;
  input.disabled = true;
  input.classList.remove('incorrect', 'correct');
  input.classList.add('hinted');
  input.setAttribute('aria-readonly', 'true');
  locked[row][col] = true;
}

async function submitMove(input) {
  const value = Number(input.value);
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const message = document.getElementById('message');
  let response;
  let result;
  try {
    response = await fetch('/move', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({row, col, value}),
    });
    result = await response.json();
  } catch (error) {
    input.value = '';
    input.classList.add('incorrect');
    input.setAttribute('aria-invalid', 'true');
    message.textContent = 'Unable to validate that move. Please try again.';
    return;
  }

  if (!response.ok || !result.valid) {
    input.classList.add('incorrect');
    input.setAttribute('aria-invalid', 'true');
    message.textContent = result.error || 'That number is not correct.';
    return;
  }

  input.classList.remove('incorrect');
  input.classList.add('correct');
  input.setAttribute('aria-invalid', 'false');
  if (result.completed) {
    showCompletion(message);
  } else {
    message.textContent = '';
    message.className = '';
  }
}

async function requestHint() {
  const message = document.getElementById('message');
  let response;
  let result;
  try {
    response = await fetch('/hint', {method: 'POST'});
    result = await response.json();
  } catch (error) {
    message.textContent = 'Unable to get a hint. Please try again.';
    return;
  }

  if (!response.ok) {
    message.textContent = result.error || 'Unable to get a hint.';
    return;
  }

  setLockedCell(result.row, result.col, result.value);
  hintsUsed += 1;
  if (result.completed) {
    showCompletion(message);
  } else {
    message.textContent = 'One cell was filled by the hint.';
    message.className = '';
  }
}

function collectBoard() {
  const inputs = document
    .getElementById('sudoku-board')
    .getElementsByTagName('input');
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const value = inputs[row * SIZE + col].value;
      board[row][col] = value ? Number(value) : 0;
    }
  }
  return {board, inputs};
}

async function checkSolution() {
  const {board, inputs} = collectBoard();
  const message = document.getElementById('message');
  let response;
  let result;
  try {
    response = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board}),
    });
    result = await response.json();
  } catch (error) {
    message.textContent = 'Unable to check the puzzle. Please try again.';
    return;
  }

  if (!response.ok) {
    message.textContent = result.error || 'Unable to check the puzzle.';
    return;
  }

  const incorrect = new Set(
    result.incorrect.map(([row, col]) => row * SIZE + col)
  );
  for (let index = 0; index < inputs.length; index++) {
    const input = inputs[index];
    if (input.disabled) continue;
    input.classList.remove('incorrect', 'correct');
    input.removeAttribute('aria-invalid');
    if (incorrect.has(index)) {
      input.classList.add('incorrect');
      input.setAttribute('aria-invalid', 'true');
    } else if (input.value) {
      input.classList.add('correct');
      input.setAttribute('aria-invalid', 'false');
    }
  }

  if (result.completed) {
    showCompletion(message);
  } else if (incorrect.size) {
    message.textContent = 'Some entries are incorrect.';
    message.className = '';
  } else {
    message.textContent = 'Keep going!';
    message.className = '';
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.givens);
  locked = data.givens.map(row => row.slice());
  hintsUsed = 0;
  gameCompleted = false;
  startTimer();
  const message = document.getElementById('message');
  message.textContent = '';
  message.className = '';
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(localStorage.getItem(THEME_KEY) || 'light');
  renderLeaderboard();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('difficulty').addEventListener('change', newGame);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  // initialize
  newGame();
});
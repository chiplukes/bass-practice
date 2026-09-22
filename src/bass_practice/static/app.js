/* bass-practice frontend */
(function () {
  "use strict";

  // ------------------------------------------------------------------
  // helpers
  // ------------------------------------------------------------------
  const $ = (sel) => document.querySelector(sel);

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function api(path, options) {
    const res = await fetch(path, options);
    if (!res.ok) {
      throw new Error(`API ${path} failed: ${res.status}`);
    }
    return res.json();
  }

  async function apiPost(path, body) {
    return api(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // ------------------------------------------------------------------
  // tab switching
  // ------------------------------------------------------------------
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
      btn.classList.add("active");
      $("#view-" + btn.dataset.view).classList.add("active");
    });
  });

  // ------------------------------------------------------------------
  // sound toggle
  // ------------------------------------------------------------------
  const soundToggle = $("#sound-toggle");
  soundToggle.checked = BassAudio.isEnabled();
  soundToggle.addEventListener("change", () => BassAudio.setEnabled(soundToggle.checked));
  $("#sound-test").addEventListener("click", () => {
    BassAudio.unlock();
    BassAudio.playTone(440.0, { duration: 0.6 });
  });

  // Unlock audio on every pointer gesture (cheap when already running).
  document.addEventListener("pointerdown", () => BassAudio.unlock());

  // ------------------------------------------------------------------
  // shared study-card rendering (note/tab/notation/fretboard)
  // ------------------------------------------------------------------
  function renderStudy({ prefix, noteNames, tabPositions, fretboardPositions, show }) {
    const noteEl = $(`#${prefix}-note-name`);
    const tabEl = $(`#${prefix}-tab`);
    const notEl = $(`#${prefix}-notation`);
    const fbEl = $(`#${prefix}-fretboard-helper`);

    noteEl.style.display = show.note ? "" : "none";
    tabEl.style.display = show.tab ? "" : "none";
    notEl.style.display = show.notation ? "" : "none";
    fbEl.style.display = show.fretboard ? "" : "none";

    if (show.note) noteEl.textContent = noteNames.length ? noteNames.join(" + ") : "rest";
    if (show.notation && noteNames.length) {
      notEl.innerHTML = "";
      Notation.renderNote(notEl, noteNames);
    }
    if (show.tab && tabPositions.length) {
      tabEl.innerHTML = "";
      Notation.renderTab(tabEl, tabPositions);
    }
    if (show.fretboard && fbLayout && fretboardPositions.length) {
      fbEl.innerHTML = "";
      renderFretboardHelper(fbEl, fbLayout, fretboardPositions);
    }
  }

  function studyShow(prefix) {
    return {
      note: $(`#${prefix}-show-note`).checked,
      tab: $(`#${prefix}-show-tab`).checked,
      notation: $(`#${prefix}-show-notation`).checked,
      fretboard: $(`#${prefix}-show-fretboard`).checked,
    };
  }

  // ------------------------------------------------------------------
  // flashcards
  // ------------------------------------------------------------------
  const fcToggle = $("#fc-toggle");
  const fcPauseBtn = $("#fc-pause");
  let fcRunning = false;
  let fcPaused = false;
  let fcCards = [];
  let fcToken = 0;

  async function fcWaitIfPaused(token) {
    while (fcPaused && fcRunning && token === fcToken) {
      await sleep(100);
    }
  }

  function fcRender(card) {
    renderStudy({
      prefix: "fc",
      noteNames: [card.name],
      tabPositions: [{ string: card.string, fret: card.fret }],
      fretboardPositions: card.positions,
      show: studyShow("fc"),
    });
  }

  function fcRenderIdle() {
    $("#fc-note-name").textContent = "Press Start";
    $("#fc-note-name").style.display = "";
    $("#fc-notation").innerHTML = "";
    $("#fc-tab").innerHTML = "";
    $("#fc-fretboard-helper").innerHTML = "";
  }

  async function fcRun() {
    const token = ++fcToken;
    fcRunning = true;
    fcPaused = false;
    fcToggle.textContent = "Stop";
    fcPauseBtn.disabled = false;
    fcPauseBtn.textContent = "Pause";
    await Notation.ready;
    const [start, end] = $("#fc-range").value.split("|");
    const res = await api(`/api/flashcards?start=${start}&end=${end}&max_fret=12`);
    fcCards = shuffle(res.cards);
    let i = 0;
    while (fcRunning && token === fcToken) {
      const card = fcCards[i % fcCards.length];
      i++;
      fcRender(card);
      await fcWaitIfPaused(token);
      const secs = parseFloat($("#fc-seconds").value);
      await sleep((Number.isFinite(secs) && secs > 0 ? secs : 2) * 1000);
      if (!fcRunning || token !== fcToken) break;
      await fcWaitIfPaused(token);
      BassAudio.playTone(card.frequency, { duration: 1.0 });
      await sleep(400);
    }
    fcPauseBtn.disabled = true;
    fcPauseBtn.textContent = "Pause";
    fcPaused = false;
  }

  fcToggle.addEventListener("click", () => {
    if (fcRunning) {
      fcRunning = false;
      fcPaused = false;
      fcToken++;
      fcToggle.textContent = "Start";
      fcPauseBtn.disabled = true;
      fcPauseBtn.textContent = "Pause";
      fcRenderIdle();
    } else {
      fcRun();
    }
  });

  fcPauseBtn.addEventListener("click", () => {
    if (!fcRunning) return;
    fcPaused = !fcPaused;
    fcPauseBtn.textContent = fcPaused ? "Resume" : "Pause";
  });

  // ------------------------------------------------------------------
  // song player
  // ------------------------------------------------------------------
  let song = null;
  let songIdx = 0;
  let songPlaying = false;

  function songStepDuration() {
    const bpm = parseInt($("#song-bpm").value, 10);
    const speed = parseFloat($("#song-speed").value);
    return (60000 / (bpm * speed)) / 1000; // seconds
  }

  function setSongPlaying(playing) {
    songPlaying = playing;
    $("#song-play").textContent = playing ? "Pause" : "Play";
  }

  function songRenderStep(play = true) {
    const step = song.steps[songIdx];
    const positions = step.notes
      .filter((n) => n.string != null && n.fret != null)
      .map((n) => ({ string: n.string, fret: n.fret }));
    renderStudy({
      prefix: "song",
      noteNames: step.notes.map((n) => n.note_name),
      tabPositions: positions,
      fretboardPositions: positions,
      show: studyShow("song"),
    });
    $("#song-progress").textContent = `step ${songIdx + 1} / ${song.steps.length}`;
    if (play) {
      const duration = Math.max(0.4, songStepDuration());
      step.notes.forEach((n) => BassAudio.playTone(n.frequency, { duration }));
    }
  }

  function songLoopBounds() {
    const total = song.steps.length;
    const startVal = parseInt($("#song-loop-start").value, 10);
    const endVal = parseInt($("#song-loop-end").value, 10);
    const start = isNaN(startVal) ? 0 : Math.max(0, Math.min(startVal - 1, total - 1));
    const end = isNaN(endVal) ? total - 1 : Math.max(start, Math.min(endVal - 1, total - 1));
    return { start, end };
  }

  async function songLoop() {
    while (songPlaying && song) {
      try {
        songRenderStep();
      } catch (e) {
        console.error(e);
      }
      await sleep(songStepDuration() * 1000);
      const { start, end } = songLoopBounds();
      songIdx = songIdx >= end ? start : songIdx + 1;
    }
  }

  $("#song-play").addEventListener("click", () => {
    if (!song) return;
    if (songPlaying) {
      setSongPlaying(false);
    } else {
      const { start, end } = songLoopBounds();
      if (songIdx < start || songIdx > end) songIdx = start;
      setSongPlaying(true);
      songLoop();
    }
  });

  $("#song-stop").addEventListener("click", () => setSongPlaying(false));

  $("#song-prev").addEventListener("click", () => {
    if (!song) return;
    setSongPlaying(false);
    const { start, end } = songLoopBounds();
    songIdx = songIdx <= start ? end : songIdx - 1;
    songRenderStep();
  });

  $("#song-next").addEventListener("click", () => {
    if (!song) return;
    setSongPlaying(false);
    const { start, end } = songLoopBounds();
    songIdx = songIdx >= end ? start : songIdx + 1;
    songRenderStep();
  });

  $("#song-load").addEventListener("click", async () => {
    song = await api(`/api/songs/${$("#song-select").value}`);
    songIdx = 0;
    setSongPlaying(false);
    songRenderStep();
  });

  // View toggles take effect immediately on the current step.
  ["note", "tab", "notation", "fretboard"].forEach((k) => {
    $(`#song-show-${k}`).addEventListener("change", () => {
      if (song) songRenderStep(false);
    });
  });

  async function loadSongList() {
    const res = await api("/api/songs");
    const sel = $("#song-select");
    sel.innerHTML = "";
    res.songs.forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = s.name;
      sel.appendChild(opt);
    });
  }

  // ------------------------------------------------------------------
  // fretboard trainer
  // ------------------------------------------------------------------
  let fbLayout = null;
  let fbTarget = null;
  let fbCorrect = 0;
  let fbAttempts = 0;

  function fbUpdateScore() {
    $("#fb-score").textContent = `${fbCorrect} / ${fbAttempts}`;
  }

  function buildFretboardTable(layout, opts) {
    const table = document.createElement("table");
    const head = document.createElement("tr");
    head.appendChild(document.createElement("th"));
    for (let fret = 1; fret <= layout.max_fret; fret++) {
      const th = document.createElement("th");
      th.textContent = String(fret);
      head.appendChild(th);
    }
    table.appendChild(head);

    // Rows high string (G) on top to low string (E) on bottom.
    // The string-label cell doubles as the open (fret 0) position.
    for (let row = layout.layout.length - 1; row >= 0; row--) {
      const tr = document.createElement("tr");
      const label = document.createElement("th");
      label.textContent = layout.string_labels[row];
      label.dataset.string = String(row);
      label.dataset.fret = "0";
      if (opts && opts.onCellClick) {
        label.addEventListener("click", () => opts.onCellClick(row, 0, label));
      }
      tr.appendChild(label);
      for (let fret = 1; fret <= layout.max_fret; fret++) {
        const td = document.createElement("td");
        td.textContent = "\u00B7";
        td.dataset.string = String(row);
        td.dataset.fret = String(fret);
        if (opts && opts.onCellClick) {
          td.addEventListener("click", () => opts.onCellClick(row, fret, td));
        }
        tr.appendChild(td);
      }
      table.appendChild(tr);
    }
    return table;
  }

  function renderFretboard() {
    const grid = $("#fb-grid");
    grid.innerHTML = "";
    grid.appendChild(buildFretboardTable(fbLayout, { onCellClick: fbClick }));
  }

  function renderFretboardHelper(container, layout, positions) {
    const marked = new Set(positions.map((p) => `${p.string}:${p.fret}`));
    // Other positions of the same pitch class (letter) are dimmed.
    const pitchClasses = new Set(
      positions.map((p) => layout.layout[p.string][p.fret].replace(/\d+$/, ""))
    );
    const table = buildFretboardTable(layout, null);
    table.querySelectorAll("[data-fret]").forEach((cell) => {
      const note = layout.layout[cell.dataset.string][cell.dataset.fret];
      const key = `${cell.dataset.string}:${cell.dataset.fret}`;
      if (marked.has(key)) {
        cell.classList.add("mark");
        cell.textContent = note;
      } else if (pitchClasses.has(note.replace(/\d+$/, ""))) {
        cell.classList.add("alt");
        cell.textContent = note;
      }
    });
    container.appendChild(table);
  }

  function fbNewNote() {
    const all = fbLayout.layout.flat();
    fbTarget = all[Math.floor(Math.random() * all.length)];
    fbAttempts++;
    fbUpdateScore();
    $("#fb-note").textContent = fbTarget;
  }

  function fbClick(string, fret, cell) {
    if (!fbTarget) return;
    const note = fbLayout.layout[string][fret];
    if (note === fbTarget) {
      fbCorrect++;
      cell.textContent = note;
      cell.classList.add("hit");
      fbNewNote();
    } else {
      cell.classList.add("miss");
      setTimeout(() => cell.classList.remove("miss"), 300);
    }
  }

  function fbReveal() {
    document.querySelectorAll("#fb-grid [data-fret]").forEach((cell) => {
      cell.textContent = fbLayout.layout[cell.dataset.string][cell.dataset.fret];
    });
  }

  $("#fb-new").addEventListener("click", fbNewNote);
  $("#fb-reveal").addEventListener("click", fbReveal);

  async function loadFretboard() {
    fbLayout = await api("/api/fretboard?max_fret=12");
    renderFretboard();
    fbNewNote();
  }

  // ------------------------------------------------------------------
  // ear trainer (functional: scale degrees in a key)
  // ------------------------------------------------------------------
  const DEGREE_LABELS = { 1: "Do", 2: "Re", 3: "Mi", 4: "Fa", 5: "So", 6: "La", 7: "Ti" };
  let earExercise = null;
  let earIdx = 0;
  let earCorrect = 0;

  async function loadEarDegrees() {
    const box = $("#ear-degrees");
    box.innerHTML = "";
    Object.keys(DEGREE_LABELS).forEach((d) => {
      const label = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.value = d;
      cb.checked = true;
      label.appendChild(cb);
      label.appendChild(document.createTextNode(` ${d} ${DEGREE_LABELS[d]}`));
      box.appendChild(label);
    });
  }

  async function loadEarRoots() {
    const res = await api("/api/notes?start=E2&end=A3");
    const sel = $("#ear-root");
    sel.innerHTML = "";
    res.notes.forEach((n) => {
      const opt = document.createElement("option");
      opt.value = n.name;
      opt.textContent = n.name;
      if (n.name === "E2") opt.selected = true;
      sel.appendChild(opt);
    });
  }

  function selectedDegrees() {
    return Array.from(document.querySelectorAll("#ear-degrees input:checked")).map((cb) => parseInt(cb.value, 10));
  }

  function earShowQuestion() {
    const q = earExercise.questions[earIdx];
    $("#ear-question").textContent = `Question ${earIdx + 1} / ${earExercise.questions.length} (key of ${earExercise.root})`;
    const answers = $("#ear-answers");
    answers.innerHTML = "";
    const degrees = Array.from(new Set(earExercise.questions.map((x) => x.degree)));
    degrees.forEach((d) => {
      const btn = document.createElement("button");
      btn.textContent = `${DEGREE_LABELS[d]} (${d})`;
      btn.addEventListener("click", () => earAnswer(d, btn));
      answers.appendChild(btn);
    });
    $("#ear-score").textContent = `${earCorrect} correct`;
  }

  function earAnswer(degree, btn) {
    const q = earExercise.questions[earIdx];
    if (degree === q.degree) {
      earCorrect++;
      btn.classList.add("correct");
    } else {
      btn.classList.add("wrong");
    }
    $("#ear-score").textContent = `${earCorrect} correct`;
    setTimeout(() => {
      earIdx++;
      if (earIdx >= earExercise.questions.length) {
        $("#ear-question").textContent = "Exercise complete";
        $("#ear-answers").innerHTML = "";
      } else {
        earShowQuestion();
      }
    }, 600);
  }

  function earPlayKey() {
    if (!earExercise) return;
    BassAudio.playTone(earExercise.root_frequency, { duration: 1.2 });
  }

  function earPlayNote() {
    if (!earExercise) return;
    const q = earExercise.questions[earIdx];
    BassAudio.playTone(q.frequency, { duration: 1.2 });
  }

  $("#ear-new").addEventListener("click", async () => {
    const degrees = selectedDegrees();
    if (!degrees.length) return;
    earExercise = await apiPost("/api/ear/degrees", {
      root: $("#ear-root").value,
      degrees: degrees,
      count: parseInt($("#ear-count").value, 10),
    });
    earIdx = 0;
    earCorrect = 0;
    earShowQuestion();
  });

  $("#ear-play-key").addEventListener("click", earPlayKey);
  $("#ear-play").addEventListener("click", earPlayNote);

  // ------------------------------------------------------------------
  // boot
  // ------------------------------------------------------------------
  async function boot() {
    await Promise.all([loadSongList(), loadFretboard(), loadEarDegrees(), loadEarRoots()]);
  }

  boot();
})();

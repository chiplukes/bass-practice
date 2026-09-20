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

  // Unlock audio on the first user gesture.
  document.addEventListener("click", () => BassAudio.unlock(), { once: true });

  // ------------------------------------------------------------------
  // flashcards
  // ------------------------------------------------------------------
  const fcToggle = $("#fc-toggle");
  let fcRunning = false;
  let fcCards = [];

  function fcRender(card) {
    const showNote = $("#fc-show-note").checked;
    const showTab = $("#fc-show-tab").checked;
    const showNotation = $("#fc-show-notation").checked;
    const showFretboard = $("#fc-show-fretboard").checked;

    $("#fc-note-name").style.display = showNote ? "" : "none";
    $("#fc-notation").style.display = showNotation ? "" : "none";
    $("#fc-tab").style.display = showTab ? "" : "none";
    $("#fc-fretboard-helper").style.display = showFretboard ? "" : "none";

    if (showNote) $("#fc-note-name").textContent = card.name;
    if (showNotation) {
      const el = $("#fc-notation");
      el.innerHTML = "";
      Notation.renderNote(el, card.name);
    }
    if (showTab) {
      const el = $("#fc-tab");
      el.innerHTML = "";
      Notation.renderTab(el, card.string, card.fret);
    }
    if (showFretboard && fbLayout) {
      const el = $("#fc-fretboard-helper");
      el.innerHTML = "";
      renderFretboardHelper(el, fbLayout, card.positions);
    }
  }

  function fcRenderIdle() {
    $("#fc-note-name").textContent = "Press Start";
    $("#fc-note-name").style.display = "";
    $("#fc-notation").innerHTML = "";
    $("#fc-tab").innerHTML = "";
    $("#fc-fretboard-helper").innerHTML = "";
  }

  async function fcRun() {
    fcRunning = true;
    fcToggle.textContent = "Stop";
    await Notation.ready;
    const [start, end] = $("#fc-range").value.split("|");
    const res = await api(`/api/flashcards?start=${start}&end=${end}&max_fret=12`);
    fcCards = shuffle(res.cards);
    let i = 0;
    while (fcRunning) {
      const card = fcCards[i % fcCards.length];
      i++;
      fcRender(card);
      await sleep(parseFloat($("#fc-seconds").value) * 1000);
      if (!fcRunning) break;
      BassAudio.playTone(card.frequency, { duration: 1.0 });
      await sleep(400);
    }
  }

  fcToggle.addEventListener("click", () => {
    if (fcRunning) {
      fcRunning = false;
      fcToggle.textContent = "Start";
      fcRenderIdle();
    } else {
      fcRun();
    }
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

  function songRenderStep() {
    const step = song.steps[songIdx];
    $("#song-display").textContent = step.display;
    $("#song-progress").textContent = `step ${songIdx + 1} / ${song.steps.length}`;
    if (step.kind === "note") {
      BassAudio.playTone(step.frequency, { duration: Math.max(0.4, songStepDuration()) });
    }
  }

  async function songLoop() {
    while (songPlaying && song) {
      songRenderStep();
      await sleep(songStepDuration() * 1000);
      songIdx = (songIdx + 1) % song.steps.length;
    }
  }

  $("#song-play").addEventListener("click", () => {
    if (!song) return;
    if (!songPlaying) {
      songPlaying = true;
      songLoop();
    }
  });

  $("#song-stop").addEventListener("click", () => {
    songPlaying = false;
  });

  $("#song-prev").addEventListener("click", () => {
    if (!song) return;
    songPlaying = false;
    songIdx = (songIdx - 1 + song.steps.length) % song.steps.length;
    songRenderStep();
  });

  $("#song-next").addEventListener("click", () => {
    if (!song) return;
    songPlaying = false;
    songIdx = (songIdx + 1) % song.steps.length;
    songRenderStep();
  });

  $("#song-load").addEventListener("click", async () => {
    song = await api(`/api/songs/${$("#song-select").value}`);
    songIdx = 0;
    songPlaying = false;
    songRenderStep();
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
    for (let fret = 0; fret <= layout.max_fret; fret++) {
      const th = document.createElement("th");
      th.textContent = fret === 0 ? "open" : String(fret);
      head.appendChild(th);
    }
    table.appendChild(head);

    // Rows high string (G) on top to low string (E) on bottom.
    for (let row = layout.layout.length - 1; row >= 0; row--) {
      const tr = document.createElement("tr");
      const label = document.createElement("th");
      label.textContent = layout.string_labels[row];
      tr.appendChild(label);
      for (let fret = 0; fret <= layout.max_fret; fret++) {
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
    const table = buildFretboardTable(layout, null);
    table.querySelectorAll("td").forEach((td) => {
      const key = `${td.dataset.string}:${td.dataset.fret}`;
      if (marked.has(key)) {
        td.classList.add("mark");
        td.textContent = layout.layout[td.dataset.string][td.dataset.fret];
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
    document.querySelectorAll("#fb-grid td").forEach((td) => {
      td.textContent = fbLayout.layout[td.dataset.string][td.dataset.fret];
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
  // ear trainer
  // ------------------------------------------------------------------
  let exercise = null;
  let earIdx = 0;
  let earCorrect = 0;

  async function loadEarIntervals() {
    const intervals = await api("/api/intervals");
    const box = $("#ear-intervals");
    box.innerHTML = "";
    intervals.forEach((name) => {
      const label = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.value = name;
      cb.checked = name !== "unison";
      label.appendChild(cb);
      label.appendChild(document.createTextNode(" " + name));
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

  function selectedIntervals() {
    return Array.from(document.querySelectorAll("#ear-intervals input:checked")).map((cb) => cb.value);
  }

  function earShowQuestion() {
    const q = exercise.questions[earIdx];
    $("#ear-question").textContent = `Question ${earIdx + 1} / ${exercise.questions.length}`;
    const answers = $("#ear-answers");
    answers.innerHTML = "";
    const names = Array.from(new Set(exercise.questions.map((x) => x.interval)));
    names.forEach((name) => {
      const btn = document.createElement("button");
      btn.textContent = name;
      btn.addEventListener("click", () => earAnswer(name, btn));
      answers.appendChild(btn);
    });
    $("#ear-score").textContent = `${earCorrect} correct`;
  }

  function earAnswer(name, btn) {
    const q = exercise.questions[earIdx];
    if (name === q.interval) {
      earCorrect++;
      btn.classList.add("correct");
    } else {
      btn.classList.add("wrong");
    }
    $("#ear-score").textContent = `${earCorrect} correct`;
    setTimeout(() => {
      earIdx++;
      if (earIdx >= exercise.questions.length) {
        $("#ear-question").textContent = "Exercise complete";
        $("#ear-answers").innerHTML = "";
      } else {
        earShowQuestion();
      }
    }, 600);
  }

  function earPlay() {
    if (!exercise) return;
    const q = exercise.questions[earIdx];
    BassAudio.playTone(q.low_frequency, { duration: 0.6 });
    setTimeout(() => BassAudio.playTone(q.high_frequency, { duration: 0.6 }), 550);
  }

  $("#ear-new").addEventListener("click", async () => {
    const intervals = selectedIntervals();
    if (intervals.length === 0) return;
    exercise = await apiPost("/api/ear/exercise", {
      intervals: intervals,
      root: $("#ear-root").value,
      count: parseInt($("#ear-count").value, 10),
      descending: $("#ear-desc").checked,
    });
    earIdx = 0;
    earCorrect = 0;
    earShowQuestion();
  });

  $("#ear-play").addEventListener("click", earPlay);

  // ------------------------------------------------------------------
  // boot
  // ------------------------------------------------------------------
  async function boot() {
    await Promise.all([loadSongList(), loadFretboard(), loadEarIntervals(), loadEarRoots()]);
  }

  boot();
})();

/* Music notation and tab rendering helpers (VexFlow + custom tab). */
(function () {
  "use strict";

  const ready = new Promise((resolve) => {
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        try {
          VexFlow.setFonts("Bravura", "Academico");
        } catch (e) {
          /* fall back to VexFlow defaults */
        }
        resolve();
      });
    } else {
      resolve();
    }
  });

  // "F#1" -> "f#/1" (VexFlow key syntax).
  function vexKey(name) {
    const m = name.match(/^([A-Ga-g])([#b]?)(-?\d+)$/);
    if (!m) return name.toLowerCase();
    return m[1].toLowerCase() + m[2] + "/" + m[3];
  }

  // Render one or more notes (a chord when more than one) on a bass-clef stave.
  function renderNote(container, names) {
    const { Renderer, Stave, StaveNote, Voice, Formatter } = VexFlow;
    const keys = names.map(vexKey);
    const div = document.createElement("div");
    div.className = "notation";
    container.appendChild(div);

    const renderer = new Renderer(div, Renderer.Backends.SVG);
    renderer.resize(200, 210);
    const ctx = renderer.getContext();

    const stave = new Stave(5, 80, 160);
    stave.addClef("bass");
    stave.setContext(ctx).draw();

    const note = new StaveNote({ keys: keys, duration: "q", clef: "bass", auto_stem: true });
    const voice = new Voice({ numBeats: 1, beatValue: 4 });
    voice.addTickable(note);
    new Formatter().joinVoices([voice]).format([voice], 150);
    voice.draw(ctx, stave);
  }

  // Render a 4-line bass tab, marking one or more string positions.
  // positions: [{ string: 0..3, fret: number }]  (0 = E lowest, 3 = G highest)
  function renderTab(container, positions) {
    const labels = ["E", "A", "D", "G"];
    const byString = {};
    positions.forEach((p) => {
      byString[p.string] = p.fret;
    });
    const wrap = document.createElement("div");
    wrap.className = "tab";
    for (let s = 3; s >= 0; s--) {
      const row = document.createElement("div");
      row.className = "tab-row";
      const label = document.createElement("span");
      label.className = "tab-string";
      label.textContent = labels[s];
      row.appendChild(label);
      const line = document.createElement("span");
      line.className = "tab-line";
      if (s in byString) {
        const num = document.createElement("span");
        num.className = "tab-fret";
        num.textContent = String(byString[s]);
        line.appendChild(num);
      }
      row.appendChild(line);
      wrap.appendChild(row);
    }
    container.appendChild(wrap);
  }

  window.Notation = { ready, renderNote, renderTab };
})();

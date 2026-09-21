/* Web Audio bass synthesizer with a global mute toggle. */
(function () {
  "use strict";

  let ctx = null;
  let enabled = true;

  try {
    enabled = localStorage.getItem("bass.sound") !== "off";
  } catch (e) {
    enabled = true;
  }

  function ensureContext() {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      ctx = new AC();
    }
    return ctx;
  }

  function unlock() {
    const c = ensureContext();
    if (c.state === "suspended") {
      c.resume();
    }
    return c;
  }

  function schedule(c, freq, opts) {
    const o = opts || {};
    const t0 = c.currentTime + (o.when || 0);
    const duration = o.duration || 0.8;
    const volume = o.volume == null ? 0.5 : o.volume;
    const release = 0.15;
    const end = t0 + duration;

    const osc = c.createOscillator();
    osc.type = o.wave || "triangle";
    osc.frequency.value = freq;

    const gain = c.createGain();
    gain.gain.setValueAtTime(0, t0);
    gain.gain.linearRampToValueAtTime(volume, t0 + 0.01);
    gain.gain.setValueAtTime(volume, Math.max(t0 + 0.02, end - release));
    gain.gain.linearRampToValueAtTime(0, end + release);

    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(t0);
    osc.stop(end + release);
  }

  function playTone(freq, opts) {
    if (!enabled || !freq || freq <= 0) {
      return;
    }
    const c = ensureContext();
    if (c.state === "suspended") {
      // Schedule only after resume completes (fixes first-gesture race).
      c.resume()
        .then(() => schedule(c, freq, opts))
        .catch(() => {});
    } else {
      schedule(c, freq, opts);
    }
  }

  function setEnabled(value) {
    enabled = !!value;
    try {
      localStorage.setItem("bass.sound", enabled ? "on" : "off");
    } catch (e) {
      /* ignore */
    }
  }

  function isEnabled() {
    return enabled;
  }

  window.BassAudio = { unlock, playTone, setEnabled, isEnabled };
})();

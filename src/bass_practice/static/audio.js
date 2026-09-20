/* Web Audio bass synthesizer. */
(function () {
  "use strict";

  let ctx = null;

  function ensureContext() {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      ctx = new AC();
    }
    if (ctx.state === "suspended") {
      ctx.resume();
    }
    return ctx;
  }

  function midiToFreq(midi) {
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  /**
   * Play a note by MIDI number.
   * opts: { when=0, duration=0.8, wave='triangle', volume=0.5 }
   */
  function playMidi(midi, opts) {
    const o = opts || {};
    const freq = midiToFreq(midi);
    const wave = o.wave || "triangle";
    playTone(freq, { when: o.when || 0, duration: o.duration || 0.8, wave: wave, volume: o.volume == null ? 0.5 : o.volume });
  }

  function playTone(freq, opts) {
    const o = opts || {};
    const c = ensureContext();
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

  function unlock() {
    ensureContext();
  }

  window.BassAudio = { unlock, playMidi, playTone, midiToFreq };
})();

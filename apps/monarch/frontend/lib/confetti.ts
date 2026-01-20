// Confetti celebration for successful generation
import confetti from "canvas-confetti";

const INK = "#1c1c1c";
const GOLD = "#c9a227";
const PAPER = "#f8f6f1";

export function triggerCelebration(): void {
  // Main burst
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: [GOLD, INK, PAPER],
    shapes: ["square", "circle"],
    scalar: 1.2,
  });

  // Side bursts with slight delay
  setTimeout(() => {
    confetti({
      particleCount: 50,
      angle: 60,
      spread: 55,
      origin: { x: 0, y: 0.65 },
      colors: [GOLD, INK],
    });
  }, 100);

  setTimeout(() => {
    confetti({
      particleCount: 50,
      angle: 120,
      spread: 55,
      origin: { x: 1, y: 0.65 },
      colors: [GOLD, INK],
    });
  }, 200);
}

export function triggerSmallCelebration(): void {
  confetti({
    particleCount: 30,
    spread: 50,
    origin: { y: 0.7 },
    colors: [GOLD, INK],
    scalar: 0.8,
    gravity: 1.2,
  });
}

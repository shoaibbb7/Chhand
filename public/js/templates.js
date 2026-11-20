/**
 * Meter templates and pattern validation.
 */

export const METERS = {
  doha: {
    name: "doha",
    devanagariName: "दोहा",
    englishName: "Doha",
    displayName: "दोहा (Doha)",
    targets: [13, 11, 13, 11],
    patternDisplay: "13 · 11 · 13 · 11",
    description: "Write traditional Hindi couplets using four charans.",
    charanCount: 4,
  },
  chaupai: {
    name: "chaupai",
    devanagariName: "चौपाई",
    englishName: "Chaupai",
    displayName: "चौपाई (Chaupai)",
    targets: [16, 16, 16, 16],
    patternDisplay: "16 · 16 · 16 · 16",
    description: "Write four rhythmic segments, each following a 16-matra target.",
    charanCount: 4,
  },
  custom: {
    name: "custom",
    devanagariName: "कस्टम छंद",
    englishName: "Custom",
    displayName: "कस्टम छंद (Custom)",
    targets: [12, 12, 14, 12],
    patternDisplay: "12 · 12 · 14 · 12",
    description: "Create your own rhythm by defining the matra count for each segment.",
    charanCount: 4,
  },
};

export function parseCustomPattern(inputStr) {
  if (!inputStr) return null;
  const parts = inputStr.split(/[,|\s]+/).map(s => s.trim()).filter(Boolean);
  const nums = parts.map(p => parseInt(p, 10));
  if (nums.some(n => isNaN(n) || n <= 0)) {
    return null;
  }
  return nums.length > 0 ? nums : null;
}

/* Ungapped DNA consensus comparison; runs locally without dependencies. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PlasmidSequence = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const MAX_BASES = 200000;
  const MAX_REPORTED_MISMATCHES = 500;
  const complement = { A: 'T', C: 'G', G: 'C', T: 'A', N: 'N' };

  function parseSequence(text) {
    if (typeof text !== 'string') throw new Error('Sequence input must be text.');
    let lines = text.split(/\r?\n/).map(x => x.trim()).filter(Boolean);
    if (!lines.length) throw new Error('Sequence is empty.');
    if (lines[0].startsWith('>')) {
      if (lines[0].length === 1) throw new Error('FASTA header must contain an identifier.');
      if (lines.slice(1).some(x => x.startsWith('>'))) throw new Error('Only one FASTA record is supported.');
      lines = lines.slice(1);
    } else if (lines.some(x => x.startsWith('>'))) {
      throw new Error('FASTA header must be the first line.');
    }
    const seq = lines.join('').replace(/\s/g, '').toUpperCase();
    if (!seq.length) throw new Error('Sequence is empty.');
    if (seq.length > MAX_BASES) throw new Error('Sequence exceeds ' + MAX_BASES + ' bases.');
    if (/[^ACGTN]/.test(seq)) throw new Error('Unsupported DNA symbols. Allowed: A, C, G, T, N.');
    return seq;
  }

  function reverseComplement(seq) {
    return seq.split('').reverse().map(base => complement[base]).join('');
  }

  function verifySequences(referenceText, observedText, options = {}) {
    const reference = parseSequence(referenceText);
    const observed = parseSequence(observedText);
    const circular = options.circular === true;
    const result = {
      reference_length: reference.length, observed_length: observed.length,
      status: 'LENGTH_MISMATCH', orientation: null, rotation_offset: null,
      mismatch_count: null, identity_percent: null, mismatches: [],
      mismatches_truncated: false,
      method: 'Ungapped exact-base comparison (N is not a wildcard)',
      note: 'Different lengths: insertions/deletions cannot be classified without gapped alignment.'
    };
    if (reference.length !== observed.length) return result;
    const reverse = reverseComplement(observed);
    if (reference === observed || reference === reverse) {
      Object.assign(result, {
        status: 'MATCH', orientation: reference === observed ? 'forward' : 'reverse_complement',
        rotation_offset: 0, mismatch_count: 0, identity_percent: 100, note: 'Exact match.'
      });
      return result;
    }
    if (circular) {
      const doubled = reference + reference.slice(0, -1);
      const forwardOffset = doubled.indexOf(observed);
      const reverseOffset = doubled.indexOf(reverse);
      if (forwardOffset !== -1 || reverseOffset !== -1) {
        Object.assign(result, {
          status: 'MATCH', orientation: forwardOffset !== -1 ? 'forward' : 'reverse_complement',
          rotation_offset: forwardOffset !== -1 ? forwardOffset : reverseOffset,
          mismatch_count: 0, identity_percent: 100, note: 'Exact match after circular rotation.'
        });
        return result;
      }
    }
    let directCount = 0;
    let reverseCount = 0;
    for (let i = 0; i < reference.length; i++) {
      if (reference[i] !== observed[i]) directCount++;
      if (reference[i] !== reverse[i]) reverseCount++;
    }
    const useReverse = reverseCount < directCount;
    const aligned = useReverse ? reverse : observed;
    const count = useReverse ? reverseCount : directCount;
    const mismatches = [];
    for (let i = 0; i < reference.length && mismatches.length < MAX_REPORTED_MISMATCHES; i++) {
      if (reference[i] !== aligned[i])
        mismatches.push({ position: i + 1, reference: reference[i], observed: aligned[i] });
    }
    Object.assign(result, {
      status: 'MISMATCH', orientation: useReverse ? 'reverse_complement' : 'forward',
      rotation_offset: 0, mismatch_count: count,
      identity_percent: Math.round((reference.length - count) * 1000000 / reference.length) / 10000,
      mismatches: mismatches, mismatches_truncated: count > mismatches.length,
      note: circular
        ? 'Differences are relative to zero-offset coordinates; non-exact circular rotations are not aligned.'
        : 'Ungapped coordinate comparison.'
    });
    return result;
  }
  return { parseSequence, reverseComplement, verifySequences, MAX_BASES };
});

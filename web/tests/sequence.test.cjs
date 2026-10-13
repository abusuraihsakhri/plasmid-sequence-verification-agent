const test = require('node:test');
const assert = require('node:assert/strict');
const {parseSequence, verifySequences} = require('../sequence.js');

test('raw and FASTA exact match', () => {
  assert.equal(verifySequences('>expected\nACGTACGT', 'ACGTACGT').status, 'MATCH');
});
test('reverse complement', () => {
  const r = verifySequences('AAGTC', 'GACTT');
  assert.equal(r.status, 'MATCH');
  assert.equal(r.orientation, 'reverse_complement');
});
test('substitutions with one-based positions', () => {
  const r = verifySequences('AAAAC', 'AATAC');
  assert.equal(r.mismatch_count, 1);
  assert.deepEqual(r.mismatches, [{position: 3, reference: 'A', observed: 'T'}]);
});
test('circular exact rotation', () => {
  assert.equal(verifySequences('AAACCG', 'CCGAAA', {circular: true}).rotation_offset, 3);
  assert.equal(verifySequences('AAACCG', 'CCGAAA').status, 'MISMATCH');
});
test('length mismatch does not assign an indel', () => {
  const r = verifySequences('ACGT', 'ACGTT');
  assert.equal(r.status, 'LENGTH_MISMATCH');
  assert.equal(r.mismatch_count, null);
});
test('reject unsupported input', () => {
  for (const s of ['', 'ACGR', '>a\nACT\n>b\nACT', '>\nACT', 'A1G'])
    assert.throws(() => parseSequence(s));
});
test('N is not a wildcard', () => {
  assert.equal(verifySequences('ANC', 'AGC').mismatch_count, 1);
});
test('bounded report size', () => {
  const r = verifySequences('A'.repeat(1000) + 'C', 'C'.repeat(1001));
  assert.equal(r.mismatch_count, 1000);
  assert.equal(r.mismatches.length, 500);
  assert.equal(r.mismatches_truncated, true);
});

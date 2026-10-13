import pytest
from sequence_verification import parse_sequence, verify_sequences


def test_exact_and_fasta():
    assert verify_sequences(">ref\nACGT\nACGT\n", ">obs\nACGTACGT\n")["status"] == "MATCH"


def test_reverse_complement():
    report = verify_sequences("AAGTC", "GACTT")
    assert (report["status"], report["orientation"]) == ("MATCH", "reverse_complement")


def test_substitution_uses_one_based_reference_coordinates():
    report = verify_sequences("AAAAC", "AATAC")
    assert report["mismatch_count"] == 1
    assert report["mismatches"] == [{"position": 3, "reference": "A", "observed": "T"}]


def test_exact_circular_rotation():
    assert verify_sequences("AAACCG", "CCGAAA", circular=True)["rotation_offset"] == 3
    assert verify_sequences("AAACCG", "CCGAAA")["status"] == "MISMATCH"


def test_unequal_lengths_are_not_mislabeled():
    report = verify_sequences("ACGT", "ACGTT")
    assert report["status"] == "LENGTH_MISMATCH" and report["mismatch_count"] is None


@pytest.mark.parametrize("raw", ["", ">ref\nACG\n>another\nACG", "ACGR", ">\nA", "A1C"])
def test_input_validation(raw):
    with pytest.raises(ValueError):
        parse_sequence(raw)


def test_n_literal():
    assert verify_sequences("ANC", "AGC")["mismatch_count"] == 1


def test_mismatch_output_limit():
    report = verify_sequences("A" * 1000 + "C", "C" * 1001)
    assert report["mismatch_count"] == 1000
    assert len(report["mismatches"]) == 500
    assert report["mismatches_truncated"]

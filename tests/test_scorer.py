from models.candidate import Candidate


def test_candidate_model():
    c = Candidate(ip="127.0.0.1", domain="demo.local", sources=["manual:inline"])
    assert c.ip == "127.0.0.1"

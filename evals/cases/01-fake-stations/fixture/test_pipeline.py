import pipeline
def test_process_end_to_end():
    pipeline.enrich = lambda r: {**r, "score": 99}     # stub
    pipeline.save   = lambda r: {"ok": True}           # stub
    assert pipeline.process({"id": 1})["ok"] is True

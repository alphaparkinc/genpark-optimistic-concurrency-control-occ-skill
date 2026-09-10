class OCCOptimisticEngine:
    """
    Kung-Robinson OCC Engine.
    Executes txns across Read, Validation, and Write phases with backward validation.
    """
    def __init__(self):
        self.committed_history = [] # (txn_id, write_set, commit_ts)
        self.global_clock = 0
        self.storage = {}

    def begin_txn(self, txn_id):
        return {
            "txn_id": txn_id,
            "start_ts": self.global_clock,
            "read_set": set(),
            "write_set": {},
        }

    def read(self, txn, key):
        txn["read_set"].add(key)
        if key in txn["write_set"]:
            return txn["write_set"][key]
        return self.storage.get(key, None)

    def write(self, txn, key, value):
        txn["write_set"][key] = value

    def validate_and_commit(self, txn):
        # Backward Validation: Check whether any transaction that committed after our start_ts
        # has a write set that overlaps with our read set.
        start_ts = txn["start_ts"]
        read_set = txn["read_set"]

        for _, w_set, commit_ts in self.committed_history:
            if commit_ts > start_ts:
                if any(k in w_set for k in read_set):
                    return False # Validation failed: Read-Write conflict!

        # Validation passed: commit writes atomically
        self.global_clock += 1
        commit_ts = self.global_clock
        for k, v in txn["write_set"].items():
            self.storage[k] = v

        self.committed_history.append((txn["txn_id"], set(txn["write_set"].keys()), commit_ts))
        return True

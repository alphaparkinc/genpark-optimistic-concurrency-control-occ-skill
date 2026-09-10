import sys
from client import OCCOptimisticEngine

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def run():
    print(">>> Demonstrating Kung-Robinson OCC Engine...")
    engine = OCCOptimisticEngine()
    engine.storage = {"item_1": 100, "item_2": 200}

    # Txn A and Txn B start concurrently
    tx_a = engine.begin_txn("TxA")
    tx_b = engine.begin_txn("TxB")

    # TxA reads item_1 and updates item_1
    val_1 = engine.read(tx_a, "item_1")
    engine.write(tx_a, "item_1", val_1 + 50)

    # TxB reads item_1 and writes item_2
    _ = engine.read(tx_b, "item_1")
    engine.write(tx_b, "item_2", 300)

    # TxA validates and commits first
    commit_a = engine.validate_and_commit(tx_a)
    print(f"TxA commit status: {commit_a}")
    assert commit_a is True

    # TxB attempts to commit: its read_set has item_1, which TxA mutated after TxB started
    commit_b = engine.validate_and_commit(tx_b)
    print(f"TxB commit status (conflicted with TxA): {commit_b}")
    assert commit_b is False

    # Disjoint TxC should commit without conflict
    tx_c = engine.begin_txn("TxC")
    engine.read(tx_c, "item_2")
    engine.write(tx_c, "item_3", 500)
    assert engine.validate_and_commit(tx_c) is True
    print("TxC (disjoint) committed successfully.")
    print("[PASS] Kung-Robinson OCC Engine verified.")

if __name__ == "__main__":
    run()

import json
import sys
from client import OCCOptimisticEngine

engine = OCCOptimisticEngine()
active_txns = {}

def handle_rpc(line):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        rid = req.get("id")
        
        if method == "tools/list":
            tools = [
                {"name": "begin_txn", "description": "Begin a transaction"},
                {"name": "commit_txn", "description": "Validate and commit transaction"}
            ]
            return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
        elif method == "tools/call":
            tname = params.get("name")
            args = params.get("arguments", {})
            if tname == "begin_txn":
                tid = args["txn_id"]
                active_txns[tid] = engine.begin_txn(tid)
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"status": "started", "txn_id": tid}})
            elif tname == "commit_txn":
                tid = args["txn_id"]
                success = engine.validate_and_commit(active_txns.pop(tid))
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"committed": success}})
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(handle_rpc(line.strip()), flush=True)

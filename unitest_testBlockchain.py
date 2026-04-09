import unittest
import hashlib
from unittest.mock import patch, MagicMock
from blockchaintest import Blockchain, DIFFICULTY



def make_bc():
    return Blockchain()

def make_bc_with_blocks():
    bc = Blockchain()
    bc.new_transaction("Alice", "Bob", 50)
    proof = bc.proof_of_work(bc.last_block["proof"])
    bc.new_block(proof)
    bc.new_transaction("Bob", "Charlie", 25)
    proof = bc.proof_of_work(bc.last_block["proof"])
    bc.new_block(proof)
    return bc

def build_longer_chain():
    other = Blockchain()
    for _ in range(3):
        proof = other.proof_of_work(other.last_block["proof"])
        other.new_block(proof)
    return other.chain


class TestInit(unittest.TestCase):
    
    def setUp(self): self.bc = make_bc()
    
    def test_genesis_block_created(self): self.assertEqual(len(self.bc.chain), 1)
    
    def test_genesis_block_structure(self):
        g = self.bc.chain[0]
        self.assertEqual(g["index"], 1); self.assertEqual(g["proof"], 100)
        self.assertEqual(g["previous_hash"], "1"); self.assertEqual(g["transactions"], [])
    
    def test_current_transactions_empty(self): self.assertEqual(self.bc.current_transactions, [])
    
    def test_nodes_empty(self): self.assertEqual(self.bc.nodes, set())


class TestTransactions(unittest.TestCase):
    
    def setUp(self): self.bc = make_bc()
    
    def test_valid_transaction_added(self):
        index = self.bc.new_transaction("Alice", "Bob", 10)
        self.assertEqual(len(self.bc.current_transactions), 1); self.assertEqual(index, 2)
    
    def test_transaction_content(self):
        self.bc.new_transaction("Alice", "Bob", 42.5)
        tx = self.bc.current_transactions[0]
        self.assertEqual(tx["sender"], "Alice"); self.assertEqual(tx["amount"], 42.5)
    
    def test_multiple_transactions(self):
        self.bc.new_transaction("Alice", "Bob", 10); self.bc.new_transaction("Bob", "Charlie", 5)
        self.assertEqual(len(self.bc.current_transactions), 2)
    
    def test_transaction_cleared_after_new_block(self):
        self.bc.new_transaction("Alice", "Bob", 10)
        proof = self.bc.proof_of_work(self.bc.last_block["proof"])
        self.bc.new_block(proof); self.assertEqual(self.bc.current_transactions, [])
    
    def test_empty_sender_raises(self):
        with self.assertRaises(ValueError): self.bc.new_transaction("", "Bob", 10)
    
    def test_empty_recipient_raises(self):
        with self.assertRaises(ValueError): self.bc.new_transaction("Alice", "", 10)
    
    def test_zero_amount_raises(self):
        with self.assertRaises(ValueError): self.bc.new_transaction("Alice", "Bob", 0)
    
    def test_negative_amount_raises(self):
        with self.assertRaises(ValueError): self.bc.new_transaction("Alice", "Bob", -5)
    
    def test_string_amount_raises(self):
        with self.assertRaises(ValueError): self.bc.new_transaction("Alice", "Bob", "dix")
    
    def test_none_sender_raises(self):
        with self.assertRaises(ValueError): self.bc.new_transaction(None, "Bob", 10)


class TestBlocks(unittest.TestCase):
    
    def setUp(self): self.bc = make_bc()
    
    def test_new_block_increments_chain(self):
        proof = self.bc.proof_of_work(self.bc.last_block["proof"])
        self.bc.new_block(proof); self.assertEqual(len(self.bc.chain), 2)
    
    def test_new_block_has_correct_index(self):
        proof = self.bc.proof_of_work(self.bc.last_block["proof"])
        block = self.bc.new_block(proof); self.assertEqual(block["index"], 2)
    
    def test_new_block_includes_pending_transactions(self):
        self.bc.new_transaction("Alice", "Bob", 10)
        proof = self.bc.proof_of_work(self.bc.last_block["proof"])
        block = self.bc.new_block(proof)
        self.assertEqual(len(block["transactions"]), 1); self.assertEqual(block["transactions"][0]["amount"], 10)
    
    def test_new_block_links_to_previous(self):
        genesis = self.bc.last_block
        proof = self.bc.proof_of_work(genesis["proof"])
        block = self.bc.new_block(proof)
        self.assertEqual(block["previous_hash"], Blockchain.hash(genesis))
    
    def test_last_block_returns_latest(self):
        self.assertEqual(make_bc_with_blocks().last_block["index"], 3)
    
    def test_block_has_timestamp(self):
        proof = self.bc.proof_of_work(self.bc.last_block["proof"])
        block = self.bc.new_block(proof); self.assertGreater(block["timestamp"], 0)


class TestHash(unittest.TestCase):
    
    def setUp(self): self.bc = make_bc()
    
    def test_hash_is_string(self): self.assertIsInstance(Blockchain.hash(self.bc.last_block), str)
    
    def test_hash_length(self): self.assertEqual(len(Blockchain.hash(self.bc.last_block)), 64)
    
    def test_hash_deterministic(self):
        b = self.bc.last_block; self.assertEqual(Blockchain.hash(b), Blockchain.hash(b))
    
    def test_hash_changes_with_content(self):
        b = self.bc.last_block; m = {**b, "proof": 9999}
        self.assertNotEqual(Blockchain.hash(b), Blockchain.hash(m))


class TestProofOfWork(unittest.TestCase):
    
    def setUp(self): self.bc = make_bc()
    
    def test_proof_is_valid(self):
        last = self.bc.last_block["proof"]
        proof = self.bc.proof_of_work(last)
        self.assertTrue(Blockchain.valid_proof(last, proof))
    
    def test_found_proof_satisfies_difficulty(self):
        last = self.bc.last_block["proof"]
        proof = self.bc.proof_of_work(last)
        h = hashlib.sha256(f"{last}{proof}".encode()).hexdigest()
        self.assertEqual(h[:DIFFICULTY], "0" * DIFFICULTY)
    
    def test_invalid_proof_rejected(self): self.assertFalse(Blockchain.valid_proof(100, 1))


class TestChainValidation(unittest.TestCase):
    
    def test_initial_chain_is_valid(self): self.assertTrue(make_bc().is_chain_valid())
    
    def test_chain_with_blocks_is_valid(self): self.assertTrue(make_bc_with_blocks().is_chain_valid())
    
    def test_tampered_transaction_invalidates_chain(self):
        bc = make_bc_with_blocks()
        bc.chain[1]["transactions"] = [{"sender": "Hacker", "recipient": "Hacker", "amount": 9999}]
        self.assertFalse(bc.is_chain_valid())
    
    def test_tampered_previous_hash_invalidates_chain(self):
        bc = make_bc_with_blocks(); bc.chain[1]["previous_hash"] = "a" * 64
        self.assertFalse(bc.is_chain_valid())
    
    def test_tampered_proof_invalidates_chain(self):
        bc = make_bc_with_blocks(); bc.chain[1]["proof"] = 9999
        self.assertFalse(bc.is_chain_valid())
    
    def test_empty_chain_is_invalid(self): self.assertFalse(make_bc().is_chain_valid([]))
    
    def test_external_chain_validation(self):
        self.assertTrue(make_bc().is_chain_valid(make_bc_with_blocks().chain))


class TestNodes(unittest.TestCase):
    
    def setUp(self): self.bc = make_bc()
    
    def test_register_valid_node(self):
        self.bc.register_node("http://192.168.1.1:5000"); self.assertIn("192.168.1.1:5000", self.bc.nodes)
    
    def test_register_multiple_nodes(self):
        self.bc.register_node("http://node1.example.com:5000"); self.bc.register_node("http://node2.example.com:5001")
        self.assertEqual(len(self.bc.nodes), 2)
    
    def test_register_duplicate_node(self):
        self.bc.register_node("http://node1.example.com:5000"); self.bc.register_node("http://node1.example.com:5000")
        self.assertEqual(len(self.bc.nodes), 1)
    
    def test_invalid_node_raises(self):
        with self.assertRaises(ValueError): self.bc.register_node("not-a-valid-url")


class TestResolveConflicts(unittest.TestCase):
    
    def test_longer_valid_chain_replaces_local(self):
        bc = make_bc(); bc.register_node("http://node1:5000"); longer = build_longer_chain()
        with patch("requests.get") as m:
            m.return_value = MagicMock(status_code=200, json=lambda: {"length": len(longer), "chain": longer})
            self.assertTrue(bc.resolve_conflicts())
        self.assertEqual(len(bc.chain), len(longer))
    
    def test_shorter_chain_does_not_replace(self):
        bc = make_bc_with_blocks(); bc.register_node("http://node1:5000"); short = Blockchain().chain
        with patch("requests.get") as m:
            m.return_value = MagicMock(status_code=200, json=lambda: {"length": len(short), "chain": short})
            self.assertFalse(bc.resolve_conflicts())
    
    def test_unreachable_node_is_skipped(self):
        import requests as req
        bc = make_bc(); bc.register_node("http://dead-node:9999")
        with patch("requests.get", side_effect=req.RequestException("timeout")):
            self.assertFalse(bc.resolve_conflicts())


if __name__ == "__main__":
    unittest.main(verbosity=2)
import hashlib
import json
import requests
from time import time
from typing import Optional
from urllib.parse import urlparse


DIFFICULTY = 4  # Nombre de zéros requis pour le proof of work


class Blockchain:
    def __init__(self):
        self.chain: list = []
        self.current_transactions: list = []
        self.nodes: set = set()
        # Création du genesis block
        self.new_block(proof=100, previous_hash="1")

    # ─────────────────────────────────────────
    # Gestion des blocs
    # ─────────────────────────────────────────

    def new_block(self, proof: int, previous_hash: Optional[str] = None) -> dict:
        """Crée un nouveau bloc et l'ajoute à la chaîne."""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self) -> dict:
        return self.chain[-1]

    # ─────────────────────────────────────────
    # Gestion des transactions
    # ─────────────────────────────────────────

    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """
        Ajoute une transaction en attente.
        Retourne l'index du bloc qui contiendra cette transaction.
        """
        if not sender or not isinstance(sender, str):
            raise ValueError("Le sender doit être une chaîne non vide.")
        if not recipient or not isinstance(recipient, str):
            raise ValueError("Le recipient doit être une chaîne non vide.")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Le montant doit être un nombre positif.")

        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        })
        return self.last_block["index"] + 1

    # ─────────────────────────────────────────
    # Proof of Work
    # ─────────────────────────────────────────

    def proof_of_work(self, last_proof: int) -> int:
        """Trouve un proof tel que hash(last_proof, proof) commence par DIFFICULTY zéros."""
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:DIFFICULTY] == "0" * DIFFICULTY

    # ─────────────────────────────────────────
    # Hashing
    # ─────────────────────────────────────────

    @staticmethod
    def hash(block: dict) -> str:
        """Retourne le hash SHA-256 d'un bloc."""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # ─────────────────────────────────────────
    # Validation de la chaîne
    # ─────────────────────────────────────────

    def is_chain_valid(self, chain: Optional[list] = None) -> bool:
        """
        Vérifie qu'une chaîne est valide :
        - chaque previous_hash correspond bien au hash du bloc précédent
        - chaque proof est valide
        Utilise self.chain par défaut.
        """
        chain = chain if chain is not None else self.chain
        if not chain:
            return False

        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

            if current["previous_hash"] != self.hash(previous):
                return False
            if not self.valid_proof(previous["proof"], current["proof"]):
                return False

        return True

    # ─────────────────────────────────────────
    # Réseau de nœuds
    # ─────────────────────────────────────────

    def register_node(self, address: str) -> None:
        """Enregistre un nouveau nœud voisin (ex: 'http://192.168.1.5:5000')."""
        parsed = urlparse(address)
        if not parsed.netloc:
            raise ValueError(f"Adresse de nœud invalide : {address}")
        self.nodes.add(parsed.netloc)

    def resolve_conflicts(self) -> bool:
        """
        Algorithme de consensus : remplace la chaîne locale par la plus longue
        chaîne valide trouvée dans le réseau.
        Retourne True si la chaîne a été remplacée.
        """
        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            try:
                response = requests.get(f"http://{node}/chain", timeout=5)
                if response.status_code != 200:
                    continue

                data = response.json()
                length = data.get("length", 0)
                chain = data.get("chain", [])

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    new_chain = chain

            except requests.RequestException:
                # Nœud injoignable, on continue
                continue

        if new_chain:
            self.chain = new_chain
            return True

        return False
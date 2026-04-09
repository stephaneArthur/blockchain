# Python Blockchain & Unit Testing 🔗🧪

## 📌 Présentation
Ce projet implémente une **Blockchain décentralisée** en Python, accompagnée d'une suite complète de **tests unitaires**. L'objectif est de démontrer les mécanismes de confiance numérique (immuabilité, minage, consensus) tout en garantissant la fiabilité du code par une couverture de tests rigoureuse.

## 🚀 Composants du projet

### 1. Le Cœur : `blockchain.py`
Le script principal définit la structure et les règles du réseau :
* **Immuabilité** : Utilisation du hashage **SHA-256** pour lier les blocs. Toute modification d'une transaction passée invalide toute la chaîne.
* **Minage (Proof of Work)** : Algorithme exigeant une puissance de calcul pour valider les nouveaux blocs (difficulté réglable).
* **Consensus Distribué** : Algorithme permettant à différents nœuds de se synchroniser et de résoudre les conflits en adoptant la chaîne la plus longue et valide.

### 2. La Suite de Tests : `unitest_testBlockchain.py`
Un framework de test robuste utilisant `unittest` pour valider chaque fonctionnalité :
* **Tests de robustesse** : Validation des transactions (montants négatifs, expéditeurs vides, etc.).
* **Tests d'intégrité** : Simulation de tentatives de falsification (altération de transaction ou de preuve) pour vérifier que la chaîne les rejette.
* **Tests de réseau (Mocking)** : Utilisation de `unittest.mock` pour simuler des réponses de nœuds distants sans nécessiter de connexion réseau réelle.

## 📊 Fonctionnalités testées
* ✅ Création correcte du bloc de genèse (Genesis Block).
* ✅ Ajout et purge des transactions en attente.
* ✅ Validité mathématique de la Preuve de Travail.
* ✅ Détection automatique de corruption de données.
* ✅ Résolution de conflits entre nœuds (Algorithme de la chaîne la plus longue).

## 🛠️ Installation et Exécution

1.  **Installation des dépendances** :
    ```bash
    pip install requests
    ```

2.  **Lancer les tests unitaires** :
    ```bash
    python3 unitest_testBlockchain.py
    ```

## 👤 Développeur
**STEPHANE ARTHUR NGUINJEL NGOM** 
* Ingénieur systèmes, réseaux et cybersécurité[cite: 127].
* Spécialiste en automatisation (Python, Bash, PowerShell) et sécurité opérationnelle[cite: 137, 211].
* [cite_start]Certifié **ISO/IEC 27001:2022 Lead Auditor**[cite: 203].

## 📄 Licence
Ce projet est développé dans un but éducatif et de démonstration technique.

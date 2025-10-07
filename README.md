# StudyCockpit Élec — Public (read‑only)

Tableau de bord **lecture seule** en Streamlit (démo) : projets, circuits, BOM, et mini outil de **dimensionnement de câbles** (formules de base).  
Le code métier avancé reste **privé** : ce dépôt public ne sert que d’interface de visualisation.

## Lancer en local
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1 ; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Puis ouvrir **http://localhost:8501**.

## Données
Un **seed** non sensible est fourni : `data/seed/cockpit_demo.db`.  
Au premier démarrage, il sera copié en `data/cockpit.db` si la base n'existe pas.

## Notes
- Ce dépôt n’expose **aucun** éditeur ni logique avancée (read‑only).
- Les formules de câble sont **approximatives** et à compléter selon les normes applicables (méthode de pose, température, groupement…).

— Mise à jour : 2025-10-07

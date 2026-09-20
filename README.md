# Güdlft : tests et débogage d'une application Flask

Projet n° 11 du parcours OpenClassrooms « Développeur d'application Python » :
*Améliorez une application Web Python par des tests et du débogage*.

Ce dépôt est un fork du [dépôt de départ fourni par OpenClassrooms](https://github.com/OpenClassrooms-Student-Center/Python_Testing).
Réalisé par Freddy KHUTI, développeur Python/Django freelance : [profil GitHub](https://github.com/Freddy0ne1), [portfolio](https://freddykhuti.fr).

## Contexte

Güdlft est un prototype de plateforme de réservation : les secrétaires de clubs d'haltérophilie se connectent avec leur adresse e-mail, puis échangent les points de leur club contre des places dans des compétitions. Les données vivent dans deux fichiers JSON (`clubs.json`, `competitions.json`), sans base de données.

L'application livrée contenait plusieurs bugs signalés par les utilisateurs et ne comportait aucun test. L'objectif était double : corriger chaque bug, puis couvrir l'application par des tests unitaires, d'intégration et de performance. Chaque correction a été menée sur sa propre branche (`bug/...`, `feature/...`, `tests/...`), accompagnée de son test dans le même commit, puis intégrée dans `master`.

## Bugs corrigés

| Symptôme d'origine | Correction apportée |
|---|---|
| Un e-mail inconnu faisait planter l'application (`IndexError`). | `/showSummary` renvoie la page d'accueil avec un message d'erreur et le code 404. |
| Les points du club n'étaient pas déduits après une réservation. | Le solde du club diminue du nombre de places réservées. |
| Il était possible de réserver sur une compétition déjà passée. | Un processeur de contexte injecte `now` dans les templates ; le lien « Book Places » n'apparaît plus si la date est dépassée. |
| Un club pouvait réserver plus de 12 places sur une compétition. | `/purchasePlaces` refuse toute demande supérieure à 12 places et affiche un message flash. |
| Un club pouvait dépenser plus de points qu'il n'en possédait. | `/purchasePlaces` refuse toute demande supérieure au solde de points et affiche un message flash. |
| `/book/<competition>/<club>` plantait si le club ou la compétition n'existait pas. | Recherche sûre avec `next(..., None)` et redirection vers l'accueil avec un message flash. |
| Il n'existait aucun tableau public des points. | Nouvelle route `/pointsboard`, accessible sans connexion, qui liste les clubs et leurs points. |

## Stratégie de tests

### Tests unitaires et d'intégration (pytest)

Les tests vivent dans `tests/test_server.py` et s'appuient sur le client de test Flask (`app.test_client()`, fixture `client` avec `TESTING = True`). Le fichier `conftest.py` ajoute la racine du projet au `sys.path` pour que `server` soit importable. Les onze cas testés :

| Test | Intention |
|---|---|
| `test_connexion_avec_email_inexistant_retourne_404` | Un e-mail inconnu renvoie 404 sans lever d'exception. |
| `test_connexion_avec_email_valide_retourne_page_bienvenue` | Un e-mail connu affiche la page de bienvenue (200). |
| `test_points_du_club_sont_deduits_apres_reservation` | Le solde du club baisse exactement du nombre de places réservées. |
| `test_reservation_impossible_pour_competition_passee` | Le lien « Book Places » est absent pour une compétition passée. |
| `test_reservation_plus_de_12_places_est_bloquee` | Une demande de 15 places est refusée avec le message attendu. |
| `test_reservation_bloquee_si_points_insuffisants` | Une demande de `solde + 1` places est refusée avec le message attendu. |
| `test_tableau_points_accessible_sans_connexion` | `/pointsboard` répond 200 et affiche les clubs. |
| `test_acces_page_reservation_club_valide` | `/book` répond 200 pour un couple club/compétition valide. |
| `test_deconnexion_redirige_vers_accueil` | `/logout` redirige (302). |
| `test_acces_page_accueil` | La page d'accueil répond 200. |
| `test_redirection_si_competition_invalide` | `/book` redirige (302) si la compétition n'existe pas. |

Les tests de connexion et d'accès aux pages sont des tests d'intégration au sens où ils traversent le routage, la vue et le rendu du template. Le projet ne comporte pas de tests fonctionnels avec Selenium.

### Tests de performance (Locust)

`locustfile.py` définit un utilisateur `GudlftUser` (temps d'attente de 1 à 3 s entre deux actions) et trois tâches de même poids : affichage de l'accueil (`GET /`), affichage du tableau des points (`GET /pointsboard`) et connexion d'un club (`POST /showSummary`). Le fichier ne fixe pas de seuil codé : les temps de réponse et le taux d'erreur se lisent dans l'interface web de Locust pendant la montée en charge.

## Lancer l'application et les tests

Les outils de test (`pytest`, `coverage`, `locust`) ne figurent pas dans `requirements.txt` et s'installent à part.

```bash
python -m venv env
source env/bin/activate        # Windows : env\Scripts\activate
pip install -r requirements.txt
pip install pytest coverage locust

# Application (http://127.0.0.1:5000)
export FLASK_APP=server.py      # Windows : set FLASK_APP=server.py
flask run

# Tests
python -m pytest -q

# Couverture
coverage run --source=. --omit="env/*,tests/*,conftest.py,locustfile.py" -m pytest -q
coverage report -m

# Performance (interface sur http://localhost:8089, l'application doit tourner)
locust -f locustfile.py --host http://127.0.0.1:5000
```

## Résultats

Mesures relevées le 20 septembre 2026 avec Python 3.13 et les versions épinglées dans `requirements.txt` :

- `python -m pytest -q` : **11 tests passés**, aucun échec.
- `coverage report` : **100 % de `server.py`** (57 instructions, aucune manquante). Le rapport n'est pas versionné, il se regénère avec les commandes ci-dessus.

Note : les deux compétitions de `competitions.json` datent de 2020. Elles sont donc toutes passées, ce qui explique que le lien « Book Places » n'apparaisse jamais sur la page de bienvenue ; la réservation reste testable en appelant directement `/purchasePlaces`.

## Structure du projet

```
.
├── server.py            # application Flask : routes et règles métier
├── clubs.json           # clubs, e-mails de connexion et points
├── competitions.json    # compétitions, dates et places disponibles
├── templates/           # index, welcome, booking, pointsboard
├── tests/
│   └── test_server.py   # 11 tests pytest
├── conftest.py          # ajoute la racine du projet au sys.path
├── locustfile.py        # scénario de charge Locust
└── requirements.txt     # dépendances de l'application (Flask 1.1.2)
```

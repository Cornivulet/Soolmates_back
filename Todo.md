# Soolmates, le projet de soo races

### made by Victor NUEL, from dev no stack to full stack

- Register avec email + verif - MAIL OK Register avec FB + verif - de 2 ans

- Connexion via email ou FB Si email ou fb pas verif Toast compte pas verif

- ~~If profile pas complet => redirige vers complete profile~~ **OK**

- ~~If profile complet redirection profile~~ **OK**

- Edition de profile asynchrone ?(/update)

### Critères de matching:

- age compris dans l'interface de lfFrom et lfTo - truc en commun

- Match créé automatiquement en db quand User1 like User2 et User2 like User1

- Lister les match de User connecté (/getMatches)
- Get les infos d'un match (/getMatch/${id})
- Supprimer un match (/deleteMatch/${id})

Fake de la data avec Faker (en cours)

CI/CD ??

Mise en prod

Messenger (Django-Channel)

Partie admin / dashboard

Bannir/Gracier un utilisateur

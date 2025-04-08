# Intégration IRC pour Home Assistant

Une intégration Home Assistant qui vous permet de vous connecter à des serveurs et canaux IRC pour communiquer avec votre instance Home Assistant.

## Fonctionnalités

- Connexion aux serveurs IRC
- Rejoindre des canaux IRC
- Support du chiffrement SSL
- Support du mot de passe serveur
- Journalisation des messages entrants
- Configuration via interface graphique

## Installation

### Installation via HACS (Recommandé)

1. Ouvrez HACS dans votre instance Home Assistant
2. Allez dans la section "Intégrations"
3. Cliquez sur les trois points dans le coin supérieur droit
4. Sélectionnez "Dépôts personnalisés"
5. Ajoutez ce dépôt :
   - Dépôt : `yourusername/hairc`
   - Catégorie : Intégration
6. Cliquez sur "Ajouter"
7. Trouvez "IRC Home Assistant Integration" dans la liste
8. Cliquez sur "Installer"
9. Redémarrez Home Assistant

### Installation manuelle

1. Copiez le dossier `custom_components/hairc` dans votre dossier `custom_components` de Home Assistant
2. Redémarrez Home Assistant
3. Allez dans Intégrations dans l'interface graphique de Home Assistant
4. Cliquez sur "+ Ajouter une intégration"
5. Recherchez "IRC Home Assistant Integration"
6. Remplissez les champs suivants :
   - Serveur (serveur IRC auquel vous souhaitez vous connecter)
   - Port (par défaut 6667)
   - Pseudonyme (nom d'utilisateur du bot)
   - Canal (canal que vous souhaitez rejoindre)
   - Mot de passe (optionnel, si requis par le serveur)
   - SSL (si vous souhaitez utiliser une connexion sécurisée)

## Configuration

### Configuration YAML (optionnelle)

```yaml
# configuration.yaml
hairc:
  server: irc.example.com
  port: 6667
  nickname: homeassistant
  channel: "#homeassistant"
  password: !secret irc_password
  ssl: false
```

## Dépannage

Si vous rencontrez des problèmes de connexion :

1. Vérifiez que l'adresse du serveur est correcte
2. Confirmez que le port est correct
3. Vérifiez que le pseudonyme est disponible
4. Vérifiez si le canal existe
5. Recherchez les messages d'erreur dans le journal de Home Assistant

## Contributions

Les contributions sont les bienvenues ! Suivez ces étapes :

1. Fork le projet
2. Créez une nouvelle branche
3. Effectuez vos modifications
4. Envoyez une pull request

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails. 
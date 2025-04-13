# Intégration IRC pour Home Assistant

Cette intégration permet à Home Assistant de se connecter à un serveur IRC et permet une communication bidirectionnelle entre IRC et Home Assistant.

## Fonctionnalités

- Connexion aux serveurs IRC (avec ou sans SSL)
- Envoi et réception de messages
- Déclenchement d'automatisations basées sur les messages IRC
- Envoi de messages à IRC depuis Home Assistant
- Reconnexion automatique en cas de perte de connexion

## Installation

### Via HACS (Recommandé)

1. Ouvrez HACS dans votre instance Home Assistant
2. Allez dans la section "Intégrations"
3. Cliquez sur les trois points dans le coin supérieur droit et sélectionnez "Dépôts personnalisés"
4. Ajoutez ce dépôt : `https://github.com/sofagris/hairc`
5. Cliquez sur "Ajouter"
6. Recherchez "IRC" dans le magasin HACS
7. Cliquez sur "Installer" pour l'intégration "Home Assistant IRC"
8. Redémarrez Home Assistant

### Installation manuelle

1. Copiez le répertoire `hairc` dans votre répertoire `custom_components` de Home Assistant
2. Redémarrez Home Assistant

## Configuration

Ajoutez ce qui suit à votre `configuration.yaml` :

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: votrebot
  channel: "#votrecanal"
  ssl: true
  password: votremotdepasse  # Optionnel
```

## Utilisation

### Envoi de messages

Vous pouvez envoyer des messages à IRC en utilisant le service `hairc.send_message` :

```yaml
service: hairc.send_message
data:
  message: "Bonjour depuis Home Assistant !"
  channel: "#votrecanal"  # Optionnel, utilise le canal par défaut si non spécifié
```

### Réception de messages

Les messages IRC déclenchent l'événement `hairc_message`. Vous pouvez créer des automatisations basées sur ces événements :

```yaml
alias: "Réponse au ping IRC"
trigger:
  platform: event
  event_type: hairc_message
  event_data:
    message: "ping"
    type: public
action:
  service: hairc.send_message
  data:
    message: "pong"
```

### Message de bienvenue

Pour faire envoyer un message de bienvenue par le bot lorsqu'il rejoint un canal, ajoutez cette automatisation :

```yaml
alias: "Message de bienvenue IRC"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant à votre service. Tapez !help pour la liste des commandes"
```

## Dépannage

Si vous rencontrez des problèmes :

1. Vérifiez les messages d'erreur dans les journaux de Home Assistant
2. Vérifiez vos paramètres de serveur IRC
3. Assurez-vous que votre pare-feu autorise les connexions sortantes vers le serveur IRC
4. Vérifiez que le bot a la permission de rejoindre le canal

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails. 
# Module Julienne Javel Tours

## Description

Le module **Julienne Javel Tours** fournit des visites guidées interactives pour les modules Julienne Javel, en particulier pour le module BET (Bureau d'Études Techniques).

## Fonctionnalités

### 🎯 Tours disponibles

- **Tour Simple BET** : Présentation rapide des fonctionnalités (2 minutes)
- **Tour Avancé BET** : Découverte détaillée avec explications (5 minutes)

### 🚀 Accès rapide

- **Démo rapide** : Accessible directement depuis le menu principal BET
- **Interface de sélection** : Choisir le type de tour depuis BET → Configuration

### 🎨 Interface utilisateur

- **Styles personnalisés** avec animations et transitions fluides
- **Design responsive** adapté aux ordinateurs et mobiles
- **Messages de félicitation** avec rainbow man à la fin des tours

## Installation

### Prérequis
- Module `juliennejavel_base` installé
- Odoo 16.0 ou supérieur

### Installation
1. Placez le module dans le répertoire des addons
2. Redémarrez le serveur Odoo
3. Activez le mode développeur
4. Installez le module depuis Apps → Julienne Javel Tours

## Utilisation

### Démarrage rapide
1. Allez dans le menu **BET**
2. Cliquez sur **🚀 Démo rapide**

### Sélection du tour
1. Allez dans **BET** → **Configuration** → **🎯 Visite guidée**
2. Choisissez le type de tour
3. Cliquez sur **🚀 Démarrer le tour**

### Depuis le code
```javascript
// Démarrer un tour depuis la console développeur
odoo.loader.startTour('bet_advanced_tour');
```

## Développement

### Ajouter un nouveau tour

1. **Créer le tour JavaScript** dans `static/src/js/` :
```javascript
registry.category("web_tour.tours").add("mon_nouveau_tour", {
    test: false,
    url: "/web",
    rainbowMan: true,
    rainbowManMessage: "Félicitations !",
    steps: () => [
        {
            content: "Description de l'étape",
            trigger: "body",
            position: "bottom",
        },
    ],
});
```

2. **Ajouter l'option** dans le modèle `tour_launcher.py`
3. **Créer une action** dans les vues XML
4. **Ajouter un menu** si nécessaire

### Structure des fichiers

```
juliennejavel_tour/
├── models/
│   └── tour_launcher.py      # Modèle de sélection des tours
├── views/
│   ├── tour_launcher_views.xml  # Interface de sélection
│   └── tour_menus.xml          # Menus dans BET
├── static/src/
│   ├── js/
│   │   ├── bet_tours.js        # Définition des tours
│   │   ├── simple_tour_launcher.js  # Service de lancement
│   │   └── tour_helper.js      # Helpers et boutons automatiques
│   └── css/
│       └── tour_styles.css     # Styles personnalisés
└── security/
    └── ir.model.access.csv     # Droits d'accès
```

## Support

Pour toute question ou suggestion d'amélioration, contactez l'équipe de développement Julienne Javel.

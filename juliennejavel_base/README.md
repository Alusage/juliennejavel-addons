# Module Julienne Javel Base

## Description

Le module **Julienne Javel Base** est une extension personnalisée pour Odoo 16.0 qui améliore et adapte les fonctionnalités de gestion commerciale et comptable pour répondre aux besoins spécifiques de l'entreprise Julienne Javel.

## Fonctionnalités principales

### 🏢 Menu BET (Bureau d'Études Techniques)

Un nouveau menu principal **BET** a été ajouté pour centraliser la gestion des dossiers techniques :

#### Suivi des dossiers
- **Devis** : Visualisation et gestion des devis en cours (brouillon et envoyés) avec vue kanban par défaut
- **Commandes** : Suivi des bons de commande confirmés et livrés

#### À facturer
- Accès direct aux commandes prêtes à être facturées

#### Contacts
- Gestion centralisée des contacts clients et prospects

#### Configuration
- **Jalons** : Configuration des étapes de suivi des dossiers
- **Import Commandes** : Assistant d'import de commandes depuis fichiers Excel
- **Import Contacts** : Assistant d'import de contacts depuis fichiers Excel
- **Modèles de devis** : Gestion des modèles de devis (copié depuis le menu Ventes pour faciliter l'accès)

### 📋 Gestion enrichie des commandes et devis

#### Informations client
- **Revenu Fiscal** : Classification des clients (Très Modeste, Revenu Intermédiaire, Modeste, Revenu Supérieur)
- **Liaison TZEE** : Système de liaison entre devis et clients TZEE
  - **Devis TZEE** : Champ affiché uniquement pour les modèles Client TZEE (ID=2), filtre les devis avec modèle TZEE (ID=3)
  - **Client TZEE** : Champ affiché uniquement pour les modèles TZEE (ID=3), filtre les clients avec modèle Client TZEE (ID=2)

#### Suivi de projet
- **Jalons** : Système de suivi par étapes personnalisables
- **Gain Énergétique** : Pourcentage d'amélioration énergétique
- **Coût Total des Travaux** : Montant global du projet
- **Somme des Subventions** : Total des aides financières
- **Taux de Financement** : Pourcentage de financement
- **Délégataire** : Responsable du dossier
- **Dossier Procivis** : Lien vers le dossier externe

### 🏪 Vue Kanban améliorée

- Affichage du **modèle de devis** directement sur les cartes kanban
- **Bordures colorées** : Chaque modèle de devis a sa couleur de bordure unique (12 couleurs disponibles)
- **Effet hover** : Animation au survol pour améliorer l'interactivité
- Groupement par défaut par **jalons** pour un suivi visuel optimal
- En-têtes de colonnes fixes pour une meilleure navigation

### 💰 Gestion des paiements

#### Modes de paiement
- Intégration des modes de paiement dans les factures et règlements
- Gestion automatique des méthodes de paiement

#### Gestion SEPA
- Fonction de **refus SEPA** pour traiter les rejets de prélèvement
- Prolongation automatique des échéances en cas de refus
- Création automatique d'écritures de contrepassation

### 📊 Export comptable personnalisé

- Adaptation des libellés d'export selon le type de journal
- Intégration des modes de paiement dans les libellés
- Gestion spécifique des comptes clients (411) et produits (7xx)

### 📥 Import de données

#### Import de commandes
- Assistant d'import depuis fichiers Excel (.xlsx)
- Création automatique de commandes basées sur des modèles
- Gestion des partenaires et des lignes de commande

#### Import de contacts
- Import en masse de contacts clients
- Mise à jour automatique des informations existantes

## Installation et configuration

1. Copiez le module dans le répertoire des addons d'Odoo
2. Redémarrez le serveur Odoo
3. Activez le mode développeur
4. Allez dans Applications → Mettre à jour la liste des modules
5. Recherchez "Julienne Javel Base" et installez le module
6. (Optionnel) Installez également "Julienne Javel Tours" pour les visites guidées

## Utilisation

### Accéder au menu BET
1. Connectez-vous à Odoo
2. Le menu **BET** apparaît dans la barre de navigation principale
3. Naviguez dans les sous-menus selon vos besoins

### Configurer les jalons
1. Allez dans **BET** → **Configuration** → **Jalons**
2. Créez et configurez vos étapes de suivi
3. Associez des catégories de produits si nécessaire

### Utiliser l'import de données
1. Allez dans **BET** → **Configuration** → **Import Commandes** ou **Import Contacts**
2. Sélectionnez votre fichier Excel
3. Lancez l'import

## Support et maintenance

Ce module a été développé spécifiquement pour Julienne Javel. Pour toute question ou demande d'évolution, contactez l'équipe de développement.

**Modules complémentaires :**
- `juliennejavel_tour` : Visites guidées interactives pour découvrir les fonctionnalités BET

---

## Section technique

### Dépendances
- `account` : Gestion comptable de base
- `account_move_export` : Export des écritures comptables
- `account_payment_mode` : Modes de paiement
- `sale` : Module de vente standard
- `sales_team` : Équipes de vente
- `sale_management` : Gestion avancée des ventes
- `onchange_helper` : Utilitaires pour les onchange

### Modèles étendus
- `sale.order` : Ajout de champs métier et logique de suivi
- `res.partner` : Ajout du revenu fiscal
- `account.payment` : Gestion des refus SEPA
- `account.move.line` : Personnalisation des exports

### Nouveaux modèles
- `sale.order.state` : Gestion des jalons/étapes
- `sale.order.import` : Assistant d'import de commandes
- `sale.order.import.contact` : Assistant d'import de contacts

### Vues personnalisées
- Vue formulaire des commandes/devis enrichie
- Vue kanban avec affichage du modèle de devis
- Vue filtre avec groupement par jalons
- Vues des assistants d'import

### Structure des fichiers
```
juliennejavel_base/
├── models/           # Modèles Python
├── views/           # Vues XML et menus
├── wizards/         # Assistants d'import
├── security/        # Droits d'accès
└── __manifest__.py  # Déclaration du module
```

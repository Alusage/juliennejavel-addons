# Module Julienne Javel Base

## Description

Le module **Julienne Javel Base** est une extension personnalisée pour Odoo 16.0 qui améliore et adapte les fonctionnalités de gestion commerciale et comptable pour répondre aux besoins spécifiques de l'entreprise Julienne Javel.

## Fonctionnalités principales

### 🏢 Menu BET (Bureau d'Études Techniques)

Un nouveau menu principal **BET** a été ajouté pour centraliser la gestion des dossiers techniques avec **contrôle d'accès** par groupes d'utilisateurs :

- **BET / Utilisateurs** : Accès aux fonctionnalités de base + Ventes / Tous les documents
- **BET / Administrateur** : Accès complet (hérite des droits utilisateurs)

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

#### Nouvelles fonctionnalités de gestion
- **Archivage automatique** : Les devis peuvent être archivés/désarchivés avec workflow intelligent
- **Conditions de paiement** : Tous les nouveaux devis ont automatiquement "30 jours" comme condition de paiement
- **Jalons par défaut** : Nouveau devis démarre automatiquement au jalon "Prospect"

#### Informations client et partenaires
- **Compte de Tiers multicompany** : Référence client spécifique à chaque entreprise
- **Revenu Fiscal** : Classification des clients (Très Modeste, Revenu Intermédiaire, Modeste, Revenu Supérieur)
- **Entreprises associées** : Gestion des entreprises liées au partenaire (repositionné dans la vue principale)

#### Liaison TZEE avec workflow intelligent
- **Devis TZEE** : Création automatique de devis TZEE depuis devis client
- **Archivage automatique** : Le devis client est archivé lors de la création du devis TZEE
- **Synchronisation des jalons** : Les jalons sont synchronisés entre devis TZEE et client archivé
- **Désarchivage automatique** : Le devis client est désarchivé quand les travaux sont terminés
- **Note automatique** : Première ligne du devis TZEE contient "Pour le dossier de [Client]"

#### Suivi de projet (repositionné dans la vue principale)
- **Jalons** : Système de suivi par étapes personnalisables
- **Informations dossier** :
  - Gain Énergétique (%)
  - Coût Total des Travaux
  - Somme des Subventions
  - Taux de Financement (%)
  - Délégataire
  - Dossier Procivis (URL)

### 🔧 Gestion des lignes de commande

#### Import d'historique facilité
- **Forcer la facturation** : Case à cocher sur les lignes de commande
- **Quantités automatiques** : Force qty_delivered et qty_invoiced à la quantité commandée
- **Affichage personnalisable** : Colonne masquée par défaut, activable par l'utilisateur
- **Idéal pour l'import** : Permet d'importer des commandes partiellement facturées/livrées

### 🏪 Vue Kanban améliorée

- Affichage du **modèle de devis** directement sur les cartes kanban
- **Bordures colorées** : Chaque modèle de devis a sa couleur de bordure unique (12 couleurs disponibles)
- **Effet hover** : Animation au survol pour améliorer l'interactivité
- Groupement par défaut par **jalons** pour un suivi visuel optimal
- En-têtes de colonnes fixes pour une meilleure navigation

### 🔍 Filtres et recherche améliorés

#### Nouveaux filtres dans les devis
- **Projets TZEE** : Affiche uniquement les devis avec modèles Client TZEE (2) et TZEE (3)
- **Archivés** : Permet de consulter les devis archivés
- Organisation claire avec séparateurs pour une meilleure lisibilité

#### Filtres dans les factures
- **Non envoyées** : Filtre les factures de vente qui n'ont pas été envoyées par email
- Améliore le suivi des communications client
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
- `sale.order` : Ajout de champs métier, logique de suivi, archivage, et workflow TZEE
- `sale.order.line` : Champ "forcer la facturation" pour l'import d'historique
- `res.partner` : Champ "Compte de Tiers" multicompany et revenu fiscal
- `account.payment` : Gestion des refus SEPA
- `account.move.line` : Personnalisation des exports
- `account.move` : Filtre pour factures non envoyées

### Nouveaux modèles
- `sale.order.state` : Gestion des jalons/étapes
- `sale.order.import` : Assistant d'import de commandes
- `sale.order.import.contact` : Assistant d'import de contacts

### Groupes de sécurité
- `group_bet_user` : Utilisateurs BET (hérite de Ventes / Tous les documents)
- `group_bet_manager` : Administrateurs BET (hérite des utilisateurs BET)

### Vues personnalisées
- Vue formulaire des commandes/devis enrichie avec informations dossier en section principale
- Vue kanban avec affichage du modèle de devis et couleurs
- Vue filtre avec groupement par jalons et nouveaux filtres (Projets TZEE, Archivés)
- Boutons d'archivage/désarchivage dans les formulaires
- Vues des assistants d'import
- Filtres de recherche améliorés pour factures

### Fonctionnalités automatisées
- **Archivage intelligent** : Archivage/désarchivage automatique des devis clients TZEE
- **Synchronisation jalons** : Maintien de la cohérence entre devis TZEE et client
- **Valeurs par défaut** : Jalon "Prospect" et conditions "30 jours" automatiques
- **Calculs dynamiques** : qty_delivered et qty_invoiced avec option "forcer facturation"

### Structure des fichiers
```
juliennejavel_base/
├── models/           # Modèles Python
├── views/           # Vues XML et menus
├── wizards/         # Assistants d'import
├── security/        # Droits d'accès
└── __manifest__.py  # Déclaration du module
```

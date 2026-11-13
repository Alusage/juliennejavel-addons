# Julienne Javel - Restriction de création de contacts et produits

Empêche la création de **contacts** et de **produits** depuis les formulaires de
**devis / commandes** et de **factures**, sauf pour les membres du groupe
**Julienne Javel / Création de contacts et produits depuis devis/factures**.

La création reste possible partout ailleurs (menu Contacts, menu Produits, etc.).
Les nouveaux utilisateurs sont restreints par défaut.

## Champs concernés

- Devis / commandes : client, produit des lignes (liste et formulaire de ligne),
  produit des produits optionnels.
- Factures : client / fournisseur, produit des lignes (liste et formulaire de ligne).

Les adresses de facturation et de livraison ne sont pas traitées : le réglage
« Adresses client » n'est pas activé chez Julienne Javel.

## Fonctionnement

Uniquement par les vues. Chaque champ est dupliqué :

- le champ d'origine reçoit `groups="<groupe créateur>"` ;
- une copie avec `options="{'no_create': True}"` est ajoutée juste après, avec
  `groups="!<groupe créateur>"`.

`no_create` masque « Créer », « Créer et modifier... » et le bouton « Nouveau »
de la fenêtre « Rechercher plus... ».

**Maintenance** : les copies reproduisent la définition des champs dans `sale`,
`sale_product_configurator`, `sale_management` et `account` (Odoo 16). Si une
mise à jour ou un nouveau module modifie ces champs, il faut reporter la
modification sur les copies.

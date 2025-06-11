/** @odoo-module **/

import { registry } from "@web/core/registry";

// Tour simple pour présenter le module BET
registry.category("web_tour.tours").add("bet_simple_tour", {
    test: false,
    url: "/web",
    rainbowMan: true,
    rainbowManMessage: "🎉 Bienvenue dans le module BET de Julienne Javel !",
    steps: () => [
        {
            content: "Bienvenue dans le module Julienne Javel Base ! Ce tour va vous présenter les principales fonctionnalités du menu BET.",
            trigger: "body",
            position: "bottom",
        },
        {
            content: "Le menu BET centralise toutes les fonctionnalités spécifiques à Julienne Javel : Suivi des dossiers, Facturation, Contacts et Configuration. Explorez chaque section pour découvrir les outils disponibles.",
            trigger: "body",
            position: "bottom",
        },
    ],
});

// Tour avancé avec navigation
registry.category("web_tour.tours").add("bet_advanced_tour", {
    test: false,
    url: "/web",
    rainbowMan: true,
    rainbowManMessage: "🎉 Félicitations ! Vous maîtrisez maintenant le module BET de Julienne Javel !",
    steps: () => [
        {
            content: "Bienvenue ! Ce tour vous présente le module Julienne Javel Base et ses fonctionnalités BET (Bureau d'Études Techniques).",
            trigger: "body",
            position: "bottom",
        },
        {
            content: "Le module BET offre 4 sections principales :<br/>• <strong>Suivi des dossiers</strong> : Devis et Commandes<br/>• <strong>À facturer</strong> : Commandes prêtes<br/>• <strong>Contacts</strong> : Gestion clients<br/>• <strong>Configuration</strong> : Paramètres et imports",
            trigger: "body",
            position: "bottom",
        },
        {
            content: "Les devis utilisent une vue kanban par défaut, groupés par jalons pour un suivi visuel optimal. Chaque carte affiche le modèle de devis utilisé.",
            trigger: "body",
            position: "bottom",
        },
        {
            content: "Les champs personnalisés incluent :<br/>• Revenu Fiscal (classification clients)<br/>• Jalons (étapes de suivi)<br/>• Gain Énergétique<br/>• Coût des Travaux<br/>• Subventions<br/>• Délégataire",
            trigger: "body",
            position: "bottom",
        },
        {
            content: "La section Configuration permet de :<br/>• Gérer les jalons<br/>• Importer des commandes depuis Excel<br/>• Importer des contacts<br/>• Lancer cette visite guidée",
            trigger: "body",
            position: "bottom",
        },
        {
            content: "Parfait ! Vous êtes maintenant prêt à utiliser le module BET. Explorez les différentes sections pour découvrir toutes les fonctionnalités disponibles.",
            trigger: "body",
            position: "bottom",
        },
    ],
});

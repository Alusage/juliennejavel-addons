/** @odoo-module **/

import { registry } from "@web/core/registry";

// Action client pour démarrer le tour
registry.category("actions").add("start_tour", (env, action) => {
    const tourName = action.params.tour_name;
    if (tourName && env.services.tour) {
        // Démarrer le tour avec le service de tour d'Odoo
        env.services.tour.startTour(tourName, {
            mode: "manual",
        });
        return Promise.resolve();
    } else {
        console.error("Service de tour non disponible ou nom de tour manquant:", tourName);
        return Promise.reject("Tour service not available");
    }
});

// Widget pour ajouter des boutons de tour dans l'interface
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter un bouton dans le menu BET si on est sur la page BET
    const addTourButton = () => {
        const betMenu = document.querySelector('[data-menu-xmlid="juliennejavel_base.menu_bet_main"]');
        if (betMenu && !document.querySelector('.o_bet_tour_helper')) {
            const tourButton = document.createElement('div');
            tourButton.className = 'o_bet_tour_helper mt-2';
            tourButton.innerHTML = `
                <div class="alert alert-info d-flex align-items-center" role="alert">
                    <i class="fa fa-info-circle me-2"></i>
                    <span class="flex-grow-1">Découvrez les fonctionnalités BET avec notre visite guidée</span>
                    <button class="btn btn-sm btn-primary ms-2" onclick="odoo.loader.startTour('bet_advanced_tour')">
                        <i class="fa fa-play me-1"></i>Démarrer
                    </button>
                </div>
            `;
            
            // Insérer après le premier élément de contenu trouvé
            const content = document.querySelector('.o_content, .o_main_content, .o_action_manager');
            if (content) {
                content.insertBefore(tourButton, content.firstChild);
            }
        }
    };

    // Observer les changements de page pour ajouter le bouton quand nécessaire
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                addTourButton();
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Ajouter le bouton immédiatement si on est déjà sur la bonne page
    setTimeout(addTourButton, 1000);
});

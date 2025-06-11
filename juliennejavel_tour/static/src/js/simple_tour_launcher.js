/** @odoo-module **/

import { registry } from "@web/core/registry";

// Action simple pour démarrer un tour sans passer par un service personnalisé
registry.category("actions").add("simple_tour_launcher", (env, action) => {
    const tourName = action.params && action.params.tour_name;
    if (tourName) {
        // Utiliser setTimeout pour s'assurer que l'interface est prête
        setTimeout(() => {
            if (env.services.tour) {
                try {
                    env.services.tour.startTour(tourName);
                } catch (error) {
                    console.error("Erreur lors du démarrage du tour:", error);
                    // Fallback : afficher une notification
                    if (env.services.notification) {
                        env.services.notification.add(
                            `Tour "${tourName}" non disponible`,
                            { type: "warning" }
                        );
                    }
                }
            }
        }, 100);
    }
    return Promise.resolve();
});

/** @odoo-module **/

import { Component, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

/**
 * Company Navbar Color Manager
 * Applies custom navbar colors based on current company
 */
export class NavbarColorService {
    constructor(env, services) {
        this.env = env;
        this.orm = services.orm;
        this.company = services.company;
        this.setupNavbarColors();
        this.setupCompanyChangeListener();
    }

    /**
     * Apply navbar colors for the current company
     */
    async setupNavbarColors() {
        try {
            const companyId = this.company.currentCompany.id;
            const colors = await this.orm.call(
                'res.company',
                'get_navbar_colors',
                [companyId]
            );

            if (colors && colors.use_custom) {
                this.applyNavbarColors(colors.navbar_bg, colors.navbar_text);
            } else {
                this.removeNavbarColors();
            }
        } catch (error) {
            console.error('Error loading navbar colors:', error);
        }
    }

    /**
     * Listen for company changes and update navbar colors
     */
    setupCompanyChangeListener() {
        // Listen to company changes
        this.company.addEventListener('company-changed', async () => {
            await this.setupNavbarColors();
        });
    }

    /**
     * Apply custom colors to the navbar
     */
    applyNavbarColors(bgColor, textColor) {
        const root = document.documentElement;

        // Set CSS custom properties for navbar colors
        root.style.setProperty('--cpss-navbar-bg', bgColor);
        root.style.setProperty('--cpss-navbar-text', textColor);

        // Add class to indicate custom navbar colors are active
        document.body.classList.add('cpss-custom-navbar-colors');

        console.log(`Applied navbar colors: bg=${bgColor}, text=${textColor}`);
    }

    /**
     * Remove custom navbar colors
     */
    removeNavbarColors() {
        const root = document.documentElement;
        root.style.removeProperty('--cpss-navbar-bg');
        root.style.removeProperty('--cpss-navbar-text');
        document.body.classList.remove('cpss-custom-navbar-colors');
    }
}

export const navbarColorService = {
    dependencies: ["orm", "company"],
    start(env, services) {
        return new NavbarColorService(env, services);
    },
};

registry.category("services").add("navbar_color", navbarColorService);

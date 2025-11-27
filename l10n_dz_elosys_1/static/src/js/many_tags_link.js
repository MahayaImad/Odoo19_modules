/** @odoo-module **/

import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

/**
 * Patch Many2ManyTagsField to add click functionality on tags
 * This allows opening the related record in a form view when clicking on a tag
 */
patch(Many2ManyTagsField.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
    },

    /**
     * Handle click on a tag badge to open the record
     * @param {MouseEvent} ev
     * @param {Object} record
     */
    async onBadgeClick(ev, record) {
        // Check if force_color option is enabled or shift key is pressed
        if (this.props.readonly || this.props.nodeOptions?.force_color || ev.shiftKey) {
            // Use default behavior (color picker if available)
            if (super.onBadgeClick) {
                return super.onBadgeClick(ev, record);
            }
            return;
        }

        // Prevent default behavior
        ev.preventDefault();
        ev.stopPropagation();

        // Open the record in a dialog form view
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.relation,
            res_id: record.resId,
            views: [[false, "form"]],
            target: "new",
            context: this.props.context,
        }, {
            onClose: async () => {
                // Reload the field after closing the dialog to reflect any changes
                await this.props.record.load();
            },
        });
    },
});

/* Copyright 2026 Tecnativa - Carlos Roca
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {Many2XAutocomplete} from "@web/views/fields/relational_utils";
import {_t} from "@web/core/l10n/translation";
import {makeContext} from "@web/core/context";
import {patch} from "@web/core/utils/patch";

// Since 17.0 "Create and edit..." is only offered once something is typed,
// and the typed text becomes the package name. Offer it again with an empty
// input, as in 15.0, so the package keeps its "/" default name and gets the
// sequence number when saved.
patch(Many2XAutocomplete.prototype, {
    async loadOptionsSource(request) {
        const options = await super.loadOptionsSource(...arguments);
        if (this.props.resModel !== "tms.package" || request.length) {
            return options;
        }
        const canCreateEdit =
            "createEdit" in this.activeActions
                ? this.activeActions.createEdit
                : this.activeActions.create;
        if (!canCreateEdit) {
            return options;
        }
        const startTypingIndex = options.findIndex((option) =>
            option.classList?.includes("o_m2o_start_typing")
        );
        if (startTypingIndex !== -1) {
            options.splice(startTypingIndex, 1);
        }
        options.push({
            label: _t("Create and edit..."),
            classList: "o_m2o_dropdown_option o_m2o_dropdown_option_create_edit",
            action: () =>
                this.openMany2X({
                    context: makeContext([this.props.context]),
                    nextRecordsContext: this.props.context,
                }),
        });
        return options;
    },
});

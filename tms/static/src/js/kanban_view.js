odoo.define("tms.kanban_view", function (require) {
    "use strict";

    const KanbanView = require("web.KanbanView");

    KanbanView.include({
        init() {
            this._super.apply(this, arguments);
            this.loadParams.groupsLimit =
                parseInt(this.arch.attrs.groups_limit, 10) || 10;
        },
    });
});

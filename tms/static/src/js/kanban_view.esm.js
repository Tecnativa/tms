import {KanbanArchParser} from "@web/views/kanban/kanban_arch_parser";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {patch} from "@web/core/utils/patch";

// Support the groups_limit kanban arch attribute (used by the vehicle
// planning kanban): parse it and feed it to the model, as the core
// controller hardcodes "no limit" since the OWL rewrite.
patch(KanbanArchParser.prototype, {
    parse(xmlDoc) {
        const result = super.parse(...arguments);
        const groupsLimit = xmlDoc.getAttribute("groups_limit");
        if (groupsLimit) {
            result.groupsLimit = parseInt(groupsLimit, 10);
        }
        return result;
    },
});

patch(KanbanController.prototype, {
    get modelParams() {
        const params = super.modelParams;
        if (this.props.archInfo.groupsLimit) {
            params.groupsLimit = this.props.archInfo.groupsLimit;
        }
        return params;
    },
});

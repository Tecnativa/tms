import {KanbanArchParser} from "@web/views/kanban/kanban_arch_parser";
import {patch} from "@web/core/utils/patch";

patch(KanbanArchParser.prototype, {
    parse(xmlDoc, models, modelName) {
        const result = super.parse(...arguments);
        result.groupsLimit = parseInt(models[modelName].groups_limit, 10) || 10;
        return result;
    },
});

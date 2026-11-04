/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { VendorMapAction } from "@nonprofit_event_venue/venue_map/venue_map_action";

/* global L */

// Distinct names throughout (state, methods, and a separate Leaflet
// click listener rather than overriding _onMapClick) so this patch
// composes safely alongside nonprofit_event_logistics' own facility-
// placement patch on the same VendorMapAction, regardless of which
// module's assets happen to load first - two independent Leaflet
// click listeners both fire for the same click, no super() chaining
// needed between them.
let stageIcon = null;
function getStageIcon() {
    if (!stageIcon) {
        stageIcon = L.divIcon({
            className: "o_nonprofit_stage_pin",
            html: '<div class="o_nonprofit_stage_pin_inner"></div>',
            iconSize: [18, 18],
        });
    }
    return stageIcon;
}

patch(VendorMapAction.prototype, {
    setup() {
        super.setup();
        this.state.stages = [];
        this.state.stagePlacementMode = false;
        this.state.placingStageId = null;
        this.stageLayer = null;

        onWillStart(async () => {
            const eventId =
                this.props.action.context?.event_id ||
                this.props.action.params?.event_id;
            if (!eventId) {
                return;
            }
            this.state.stages = await this.orm.searchRead(
                "event.entertainment.stage",
                [["event_id", "=", eventId]],
                ["name", "latitude", "longitude"]
            );
        });
    },

    get unplacedStages() {
        return this.state.stages.filter((s) => !s.latitude && !s.longitude);
    },

    _renderMap() {
        super._renderMap();
        if (!this.leafletMap) {
            return;
        }
        this.stageLayer = L.layerGroup().addTo(this.leafletMap);
        this._renderStageMarkers();
        this.leafletMap.on("click", (ev) => this._onStageMapClick(ev));
    },

    _renderStageMarkers() {
        this.stageLayer.clearLayers();
        for (const stage of this.state.stages) {
            if (!stage.latitude && !stage.longitude) {
                continue;
            }
            const marker = L.marker([stage.latitude, stage.longitude], {
                icon: getStageIcon(),
            }).addTo(this.stageLayer);
            marker.bindPopup(`<strong>${stage.name}</strong>`);
            marker.on("popupopen", (event) => {
                const title = event.popup.getElement()?.querySelector("strong");
                if (title) {
                    title.style.cursor = "pointer";
                    title.title = "Open this stage";
                    title.addEventListener(
                        "click", () => this._openStage(stage.id));
                }
            });
        }
    },

    toggleStagePlacementMode() {
        this.state.placingStageId = null;
        this.state.stagePlacementMode = !this.state.stagePlacementMode;
    },

    armStage(stageId) {
        this.state.placingStageId = stageId;
    },

    async _onStageMapClick(ev) {
        if (!this.state.placingStageId) {
            return;
        }
        const { lat, lng } = ev.latlng;
        await this.orm.write(
            "event.entertainment.stage", [this.state.placingStageId],
            { latitude: lat, longitude: lng });
        const stage = this.state.stages.find(
            (s) => s.id === this.state.placingStageId);
        if (stage) {
            stage.latitude = lat;
            stage.longitude = lng;
        }
        this.state.placingStageId = null;
        this._renderStageMarkers();
    },

    _openStage(stageId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "event.entertainment.stage",
            res_id: stageId,
            views: [[false, "form"]],
            target: "current",
        });
    },
});

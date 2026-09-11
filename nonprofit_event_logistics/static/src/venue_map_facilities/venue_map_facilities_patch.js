/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { VendorMapAction } from "@nonprofit_event_venue/venue_map/venue_map_action";

/* global L */

let facilityIcon = null;
function getFacilityIcon() {
    if (!facilityIcon) {
        facilityIcon = L.divIcon({
            className: "o_nonprofit_facility_pin",
            html: '<div class="o_nonprofit_facility_pin_inner"></div>',
            iconSize: [16, 16],
        });
    }
    return facilityIcon;
}

patch(VendorMapAction.prototype, {
    setup() {
        super.setup();
        this.state.facilities = [];
        this.state.placementMode = false;
        this.state.placingFacilityId = null;
        this.facilityLayer = null;

        onWillStart(async () => {
            const eventId =
                this.props.action.context?.event_id ||
                this.props.action.params?.event_id;
            if (!eventId) {
                return;
            }
            this.state.facilities = await this.orm.searchRead(
                "event.facility",
                [["event_id", "=", eventId]],
                ["name", "facility_type", "quantity", "latitude", "longitude"]
            );
        });
    },

    get unplacedFacilities() {
        return this.state.facilities.filter((f) => !f.latitude && !f.longitude);
    },

    _renderMap() {
        super._renderMap();
        if (!this.leafletMap) {
            return;
        }
        this.facilityLayer = L.layerGroup().addTo(this.leafletMap);
        this._renderFacilityMarkers();
        this.leafletMap.on("click", (ev) => this._onMapClick(ev));
    },

    _renderFacilityMarkers() {
        this.facilityLayer.clearLayers();
        for (const facility of this.state.facilities) {
            if (!facility.latitude && !facility.longitude) {
                continue;
            }
            const marker = L.marker([facility.latitude, facility.longitude], {
                icon: getFacilityIcon(),
            }).addTo(this.facilityLayer);
            marker.bindPopup(
                `<strong>${facility.name}</strong><br/>` +
                `${facility.facility_type} × ${facility.quantity}`
            );
            marker.on("popupopen", (event) => {
                const title = event.popup.getElement()?.querySelector("strong");
                if (title) {
                    title.style.cursor = "pointer";
                    title.title = "Open this facility";
                    title.addEventListener(
                        "click", () => this._openFacility(facility.id));
                }
            });
        }
    },

    togglePlacementMode() {
        this.state.placingFacilityId = null;
        this.state.placementMode = !this.state.placementMode;
    },

    armFacility(facilityId) {
        this.state.placingFacilityId = facilityId;
    },

    async _onMapClick(ev) {
        if (!this.state.placingFacilityId) {
            return;
        }
        const { lat, lng } = ev.latlng;
        await this.orm.write(
            "event.facility", [this.state.placingFacilityId],
            { latitude: lat, longitude: lng });
        const facility = this.state.facilities.find(
            (f) => f.id === this.state.placingFacilityId);
        if (facility) {
            facility.latitude = lat;
            facility.longitude = lng;
        }
        this.state.placingFacilityId = null;
        this._renderFacilityMarkers();
    },

    _openFacility(facilityId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "event.facility",
            res_id: facilityId,
            views: [[false, "form"]],
            target: "current",
        });
    },
});

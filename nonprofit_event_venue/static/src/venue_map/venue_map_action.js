/** @odoo-module **/

import { Component, onMounted, onWillStart, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

// Loaded via web.assets_backend before this file (see __manifest__.py) -
// vendored under static/lib/leaflet, not fetched from a CDN at runtime.
/* global L */

const STATE_COLOR = {
    available: "#2e6e7e",
    unavailable: "#3f7d4f",
};

export class VendorMapAction extends Component {
    static template = "nonprofit_event_venue.VendorMapAction";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.mapRef = useRef("map");
        this.state = useState({ event: null, booths: [], loading: true });
        this.leafletMap = null;

        onWillStart(async () => {
            const eventId =
                this.props.action.context?.event_id ||
                this.props.action.params?.event_id;
            if (!eventId) {
                this.state.loading = false;
                return;
            }
            const [event] = await this.orm.read(
                "event.event",
                [eventId],
                ["name", "map_origin_lat", "map_origin_lng"]
            );
            this.state.event = event;
            this.state.booths = await this.orm.searchRead(
                "event.booth",
                [["event_id", "=", eventId], ["row_id", "!=", false]],
                [
                    "name", "booth_label", "state", "partner_id",
                    "booth_category_id", "latitude", "longitude",
                ]
            );
            this.state.loading = false;
        });

        onMounted(() => this._renderMap());
    }

    _renderMap() {
        if (!this.mapRef.el || !this.state.event) {
            return;
        }
        const { map_origin_lat: lat, map_origin_lng: lng } = this.state.event;
        const center = lat || lng ? [lat, lng] : [0, 0];
        this.leafletMap = L.map(this.mapRef.el).setView(center, 19);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 21,
            attribution: "© OpenStreetMap contributors",
        }).addTo(this.leafletMap);

        const points = [];
        for (const booth of this.state.booths) {
            if (!booth.latitude && !booth.longitude) {
                continue;
            }
            const point = [booth.latitude, booth.longitude];
            points.push(point);
            const color = STATE_COLOR[booth.state] || "#6d6055";
            const marker = L.circleMarker(point, {
                radius: 9,
                color,
                weight: 2,
                fillColor: color,
                fillOpacity: 0.85,
            }).addTo(this.leafletMap);
            const renter = booth.partner_id ? booth.partner_id[1] : "unrented";
            const category = booth.booth_category_id
                ? booth.booth_category_id[1] : "";
            marker.bindPopup(
                `<strong>${booth.name}</strong><br/>` +
                `${booth.booth_label || ""}<br/>` +
                `${category}<br/>` +
                `${renter}`
            );
            marker.on("popupopen", (event) => {
                const title = event.popup.getElement()?.querySelector("strong");
                if (title) {
                    title.style.cursor = "pointer";
                    title.title = "Open this booth";
                    title.addEventListener("click", () => this._openBooth(booth.id));
                }
            });
        }
        if (points.length) {
            this.leafletMap.fitBounds(points, { padding: [30, 30] });
        }
    }

    _openBooth(boothId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "event.booth",
            res_id: boothId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("nonprofit_event_venue.vendor_map", VendorMapAction);

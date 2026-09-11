# -*- coding: utf-8 -*-
from werkzeug.urls import url_encode

from odoo import fields, http
from odoo.http import request


class ParadePortal(http.Controller):
    # Plain int ids, resolved with sudo() below, rather than the
    # <model(...)> converter: that converter looks the record up as the
    # current (public/anonymous) user, and event.event has no public read
    # rule of its own (one only appears once website_event is installed,
    # and even then it's gated on the event being published on the site -
    # not the gate we want here, since a parade application link is meant
    # to be shared directly regardless of storefront visibility).

    @http.route(
        ["/event/<int:event_id>/parade/apply"],
        type="http", auth="public", methods=["GET"], website=True, sitemap=False)
    def parade_apply_form(self, event_id, **kwargs):
        event = request.env["event.event"].sudo().browse(event_id).exists()
        if not event:
            return request.not_found()
        values = {
            "event": event,
            "msg": kwargs.get("parade_msg"),
            "ok": kwargs.get("parade_ok") == "1",
        }
        return request.render(
            "nonprofit_event_parade.parade_apply_page", values)

    @http.route(
        ["/event/<int:event_id>/parade/apply/submit"],
        type="http", auth="public", methods=["POST"], website=True,
        sitemap=False, csrf=True)
    def parade_apply_submit(self, event_id, **post):
        event = request.env["event.event"].sudo().browse(event_id).exists()
        if not event:
            return request.not_found()
        errors = self._validate(event, post)
        if errors:
            return request.render("nonprofit_event_parade.parade_apply_page", {
                "event": event, "errors": errors, "post": post,
            })

        partner = request.env["res.partner"].sudo().find_or_create(
            "%s <%s>" % (post.get("contact_name"), post.get("contact_email")))

        entry = request.env["event.parade.entry"].sudo().create({
            "event_id": event.id,
            "partner_id": partner.id,
            "name": post.get("name"),
            "org_name": post.get("org_name"),
            "contact_name": post.get("contact_name"),
            "contact_email": post.get("contact_email"),
            "contact_phone": post.get("contact_phone"),
            "entry_type": post.get("entry_type") or "walking_group",
            "participant_count": self._to_int(post.get("participant_count")),
            "vehicle_count": self._to_int(post.get("vehicle_count")),
            "linear_feet_needed": self._to_float(post.get("linear_feet_needed")),
            "sound_amplification": bool(post.get("sound_amplification")),
            "special_requirements": post.get("special_requirements"),
            "waiver_accepted": True,
            "waiver_accepted_date": fields.Datetime.now(),
        })
        template = request.env.ref(
            "nonprofit_event_parade.mail_template_parade_application_received",
            raise_if_not_found=False)
        if template:
            template.sudo().send_mail(entry.id, force_send=False)

        query = url_encode({
            "parade_ok": "1",
            "parade_msg": "Thanks! Your application for %s is in - we'll "
                          "follow up by email." % (post.get("name") or "your entry"),
        })
        return request.redirect(
            "/event/%s/parade/apply?%s" % (event.id, query))

    def _validate(self, event, post):
        errors = []
        if event.parade_entry_deadline and \
                fields.Datetime.now() > event.parade_entry_deadline:
            errors.append(
                "Applications for this parade have closed. Please contact "
                "the organizers directly.")
            return errors
        if not event.parade_enabled:
            errors.append("This event isn't accepting parade entries.")
            return errors
        if not (post.get("name") or "").strip():
            errors.append("Give your unit or contingent a name.")
        if not (post.get("contact_name") or "").strip():
            errors.append("A contact name is required.")
        if not (post.get("contact_email") or "").strip():
            errors.append("A contact email is required.")
        for field, label in (
            ("participant_count", "Participants"),
            ("vehicle_count", "Vehicles"),
            ("linear_feet_needed", "Linear feet needed"),
        ):
            value = post.get(field)
            if value not in (None, ""):
                try:
                    float(value)
                except ValueError:
                    errors.append("%s must be a number." % label)
        if not post.get("waiver_accepted"):
            errors.append(
                "You must accept the liability waiver to submit an entry.")
        return errors

    @staticmethod
    def _to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

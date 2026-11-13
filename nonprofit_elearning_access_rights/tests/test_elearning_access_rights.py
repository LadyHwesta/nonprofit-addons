# -*- coding: utf-8 -*-
import re

from odoo.tests import TransactionCase, tagged
from odoo.tools import file_path


@tagged("post_install", "-at_install")
class TestElearningAccessRights(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env.ref(
            "nonprofit_elearning_access_rights.channel_access_rights")

    def test_course_is_published_and_gated(self):
        self.assertTrue(self.channel.is_published)
        self.assertEqual(self.channel.visibility, "members")
        self.assertIn(
            self.env.ref("base.group_erp_manager"),
            self.channel.enroll_group_ids)

    def test_course_structure(self):
        sections = self.channel.slide_ids.filtered("is_category")
        self.assertEqual(len(sections), 4)
        lessons = self.channel.slide_content_ids.filtered(
            lambda s: s.slide_category == "article")
        self.assertEqual(len(lessons), 8)
        for lesson in lessons:
            self.assertTrue(lesson.category_id, "%s has no section" % lesson.name)

    def test_quiz_answers_are_valid(self):
        quiz = self.channel.slide_content_ids.filtered(
            lambda s: s.slide_category == "quiz")
        self.assertEqual(len(quiz), 1)
        self.assertEqual(len(quiz.question_ids), 4)
        for question in quiz.question_ids:
            self.assertFalse(question.answers_validation_error)
            self.assertEqual(
                len(question.answer_ids.filtered("is_correct")), 1)

    def test_core_events_lesson_matches_general_volunteer_access(self):
        lesson = self.env.ref("nonprofit_elearning_access_rights.lesson_core_events")
        self.assertIn("Registration Desk", lesson.html_content)

    def test_screenshots_exist(self):
        lesson = self.env.ref("nonprofit_elearning_access_rights.lesson_assign")
        images = re.findall(r'src="/([^"]+\.png)"', lesson.html_content)
        self.assertEqual(len(images), 3)
        for image in images:
            self.assertTrue(file_path(image))

    def test_every_lesson_is_published(self):
        """A lesson starts unpublished, so each one must say so in the data,
        or learners see the course but none of its pages."""
        data = self.env["ir.model.data"].search(
            [("module", "=", "nonprofit_elearning_access_rights"), ("model", "=", "slide.slide")])
        lessons = self.env["slide.slide"].browse(data.mapped("res_id"))
        self.assertTrue(lessons)
        self.assertFalse(lessons.filtered(lambda s: not s.is_published).mapped("name"))

# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestElearningEventEntertainment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env.ref(
            "nonprofit_elearning_event_entertainment.channel_event_entertainment")

    def test_course_is_published_and_gated(self):
        self.assertTrue(self.channel.is_published)
        self.assertEqual(self.channel.visibility, "members")
        self.assertIn(
            self.env.ref("nonprofit_event_entertainment.group_entertainment_user"),
            self.channel.enroll_group_ids)

    def test_course_structure(self):
        self.assertEqual(len(self.channel.slide_ids.filtered("is_category")), 5)
        lessons = self.channel.slide_content_ids.filtered(
            lambda s: s.slide_category == "article")
        self.assertEqual(len(lessons), 5)
        for lesson in lessons:
            self.assertTrue(lesson.category_id, "%s has no section" % lesson.name)

    def test_quiz_answers_are_valid(self):
        quiz = self.channel.slide_content_ids.filtered(
            lambda s: s.slide_category == "quiz")
        self.assertEqual(len(quiz.question_ids), 4)
        for question in quiz.question_ids:
            self.assertFalse(question.answers_validation_error)
            self.assertEqual(len(question.answer_ids.filtered("is_correct")), 1)

    def test_every_lesson_is_published(self):
        """A lesson starts unpublished, so each one must say so in the data,
        or learners see the course but none of its pages."""
        data = self.env["ir.model.data"].search(
            [("module", "=", "nonprofit_elearning_event_entertainment"), ("model", "=", "slide.slide")])
        lessons = self.env["slide.slide"].browse(data.mapped("res_id"))
        self.assertTrue(lessons)
        self.assertFalse(lessons.filtered(lambda s: not s.is_published).mapped("name"))

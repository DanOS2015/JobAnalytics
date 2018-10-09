from django.test import SimpleTestCase
from ..forms import ApplicantForm


class ApplicantFormTest(SimpleTestCase):

    def test_form_with_valid_number_without_plus(self):
        form_data = {
            'first_name': 'Form',
            'last_name': 'Test',
            'email': 'form@test.com',
            'phone_number': '0871234567',
        }
        form = ApplicantForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_valid_number_with_plus(self):
        form_data = {
            'first_name': 'Form',
            'last_name': 'Test',
            'email': 'form@test.com',
            'phone_number': '+353871234567',
        }
        form = ApplicantForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_number(self):
        form_data = {
            'first_name': 'Form',
            'last_name': 'Test',
            'email': 'form@test.com',
            'phone_number': '08712345',
        }
        form = ApplicantForm(data=form_data)
        self.assertFalse(form.is_valid())
import unittest
from types import SimpleNamespace

from app.routes import public
from app.utils import id_generator, email_service


class DummyRequest:
    def __init__(self, session=None):
        self.session = session or {}


class RegistrationSuccessFlowTests(unittest.TestCase):
    def test_consume_registration_success_returns_and_removes_session_data(self):
        request = DummyRequest({"registration_success": {"reg_id": "KNM-00001", "name": "Ada", "message": "QR sent to email"}})

        result = public._consume_registration_success(request)

        self.assertEqual(result["reg_id"], "KNM-00001")
        self.assertEqual(result["name"], "Ada")
        self.assertEqual(result["message"], "QR sent to email")
        self.assertNotIn("registration_success", request.session)

    def test_store_registration_success_persists_data_in_session(self):
        request = DummyRequest()

        public._store_registration_success(request, {"reg_id": "KNM-00002", "name": "Grace", "message": "QR sent to email"})

        self.assertEqual(request.session["registration_success"]["reg_id"], "KNM-00002")
        self.assertEqual(request.session["registration_success"]["name"], "Grace")
        self.assertEqual(request.session["registration_success"]["message"], "QR sent to email")
        self.assertNotIn("qr_path", request.session["registration_success"])

    def test_store_registration_success_includes_qr_path_for_display(self):
        request = DummyRequest()
        participant = SimpleNamespace(
            reg_id="KNM-00003",
            name="Grace",
            qr_path="/static/qrcodes/KNM-00003.png",
        )

        public._store_registration_success(request, participant)

        self.assertEqual(request.session["registration_success"]["qr_path"], "/static/qrcodes/KNM-00003.png")

    def test_calculate_next_reg_id_value_starts_at_one_when_empty(self):
        self.assertEqual(id_generator.calculate_next_reg_id_value(existing_count=0, max_reg_id=None, start_at=1), 1)

    def test_sanitize_smtp_credentials_removes_whitespace(self):
        config = email_service._get_smtp_config()
        self.assertEqual(config["username"], config["username"].strip())
        self.assertEqual(config["password"], config["password"].strip())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "mulesoft" / "north-star-twilio-webhook"


class TwilioWebhookAppTest(unittest.TestCase):
    def test_mule_app_exposes_twilio_intake_and_salesforce_bridge(self) -> None:
        config = (
            APP
            / "src"
            / "main"
            / "mule"
            / "north-star-twilio-webhook.xml"
        ).read_text()

        self.assertIn('path="/"', config)
        self.assertIn('path="/twilio/whatsapp/inbound"', config)
        self.assertIn('allowedMethods="POST"', config)
        self.assertIn('/services/apexrest/northstar/v1/twilio/whatsapp', config)
        self.assertIn('Twilio Sandbox WhatsApp', config)
        self.assertIn('variableName="responseFormat" value="twiml"', config)
        self.assertIn('Thanks. North Star received this.', config)

    def test_mule_app_exposes_meta_intake_and_webhook_verification(self) -> None:
        config = (
            APP
            / "src"
            / "main"
            / "mule"
            / "north-star-twilio-webhook.xml"
        ).read_text()

        self.assertIn('path="/"', config)
        self.assertIn('path="/meta/whatsapp/inbound"', config)
        self.assertIn('allowedMethods="GET"', config)
        self.assertIn("hub.verify_token", config)
        self.assertIn("meta.webhookVerifyToken", config)
        self.assertIn("Meta WhatsApp Cloud API", config)
        self.assertIn("contains 'json'", config)
        self.assertIn("status: \"received\"", config)

    def test_mule_app_does_not_commit_runtime_secrets(self) -> None:
        combined = "\n".join(
            path.read_text()
            for path in [
                APP / "src" / "main" / "resources" / "mule-artifact.properties",
                APP / "README.md",
            ]
        )

        self.assertNotRegex(combined, r"AC[0-9a-fA-F]{32}")
        self.assertNotRegex(
            combined, r"(?i)auth[_-]?token\s*[:=]\s*[0-9a-f]{32}"
        )
        self.assertNotIn('xoxb-', combined)
        self.assertIn('replace-at-runtime', combined)


if __name__ == "__main__":
    unittest.main()

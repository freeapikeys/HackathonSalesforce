from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "mulesoft" / "logia-twilio-webhook"


class TwilioWebhookAppTest(unittest.TestCase):
    def test_mule_app_exposes_twilio_intake_and_salesforce_bridge(self) -> None:
        config = (
            APP
            / "src"
            / "main"
            / "mule"
            / "logia-twilio-webhook.xml"
        ).read_text()

        self.assertIn('path="/"', config)
        self.assertIn('path="/twilio/whatsapp/inbound"', config)
        self.assertIn('allowedMethods="POST"', config)
        self.assertIn('/services/apexrest/logia/v1/twilio/whatsapp', config)
        self.assertIn('Twilio Sandbox WhatsApp', config)
        self.assertIn("contains 'json'", config)
        self.assertIn('Thanks. Logia received this.', config)
        self.assertIn(
            "Submitting Meta WhatsApp acknowledgement to Graph API",
            config,
        )

    def test_mule_app_exposes_meta_intake_and_webhook_verification(self) -> None:
        config = (
            APP
            / "src"
            / "main"
            / "mule"
            / "logia-twilio-webhook.xml"
        ).read_text()

        self.assertIn('path="/"', config)
        self.assertIn('path="/meta/whatsapp/inbound"', config)
        self.assertIn('allowedMethods="GET"', config)
        self.assertIn("hub.verify_token", config)
        self.assertIn("meta.webhookVerifyToken", config)
        self.assertIn("Meta WhatsApp Cloud API", config)
        self.assertIn("contains 'json'", config)
        self.assertIn("metaGraphRequest", config)
        self.assertIn("meta.whatsappPhoneNumberId", config)
        self.assertIn("meta.whatsappAccessToken", config)
        self.assertIn("Thanks. Logia received this.", config)
        self.assertIn("status: \"received\"", config)

    def test_mule_app_exposes_slack_interactivity_and_commands(self) -> None:
        config = (
            APP
            / "src"
            / "main"
            / "mule"
            / "logia-twilio-webhook.xml"
        ).read_text()

        self.assertIn('path="/slack/interactions"', config)
        self.assertIn('path="/slack/commands"', config)
        self.assertIn('allowedMethods="POST"', config)
        self.assertIn("Acknowledge Slack interaction", config)
        self.assertIn("Return Slack command help", config)
        self.assertIn("Route rewritten root POST", config)
        self.assertIn("Route shared public POST", config)
        self.assertIn("process-slack-interaction", config)
        self.assertIn("process-slack-command", config)
        self.assertIn("Salesforce remains the system of record", config)
        self.assertIn("Try `/logia status <case-id|approval-id>`", config)
        self.assertIn("`/logia queue`", config)
        self.assertIn("`/logia demo hospital|airport|hotel|bank`", config)
        self.assertIn("`/logia order <item> qty <amount>", config)
        self.assertIn("profile:airport-operations", config)
        self.assertIn("Slack mirrors safe case", config)
        self.assertIn("Protected supplier order draft", config)
        self.assertIn("SEND_VENDOR_EMAIL", config)

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
        self.assertNotIn("xo" + "xb-", combined)
        self.assertIn('replace-at-runtime', combined)


if __name__ == "__main__":
    unittest.main()

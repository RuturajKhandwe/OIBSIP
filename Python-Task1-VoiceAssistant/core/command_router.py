"""
Command Router for Intelligent Python Voice Assistant.
Orchestrates natural language understanding, entity extraction, custom command matching, and service dispatch.
"""

from typing import Tuple, Dict, Any, Optional
from core.logger import get_logger
from config import Config
from nlp.intent_engine import IntentClassifier
from services.datetime_service import DateTimeService
from services.search_service import SearchService
from services.custom_service import CustomCommandService
from services.weather_service import WeatherService
from services.knowledge_service import KnowledgeService
from services.email_service import EmailService
from services.reminder_service import ReminderService

logger = get_logger("CommandRouter")

class CommandRouter:
    """Routes user text inputs through NLU, entity extraction, custom commands, and domain services."""

    def __init__(self, intent_classifier: Optional[IntentClassifier] = None, custom_service: Optional[CustomCommandService] = None):
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.custom_service = custom_service or CustomCommandService()
        self.pending_context: Optional[Dict[str, Any]] = None

    def process_command(self, user_input: str) -> Tuple[str, bool, Dict[str, Any]]:
        """
        Processes raw user input text through the intent & entity pipeline.
        Returns a tuple of (response_text, should_exit_flag, nlu_result_dict).
        """
        if not user_input or not user_input.strip():
            return "I didn't hear anything. Please try again.", False, {"intent": "empty", "confidence": 0.0}

        clean_text = user_input.strip()

        # Step 0: Handle Pending Context Follow-up Dialogs
        if self.pending_context:
            pending_intent = self.pending_context.get("intent")

            # Follow-up for get_weather
            if pending_intent == "get_weather":
                self.pending_context = None
                city = clean_text.rstrip(".?").strip()
                logger.info(f"[CommandRouter] Handling follow-up weather city input: '{city}'")
                weather_data = WeatherService.fetch_weather_data(city)
                response = WeatherService.format_weather_response(weather_data)
                nlu_res = {
                    "intent": "get_weather",
                    "confidence": 1.0,
                    "entities": {"city": city},
                    "raw_text": clean_text
                }
                return response, False, nlu_res

            # Follow-up for send_email
            elif pending_intent == "send_email":
                stage = self.pending_context.get("stage")
                recipient = self.pending_context.get("recipient")
                subject = self.pending_context.get("subject", "Voice Assistant Message")
                body = self.pending_context.get("body")

                if stage in ("recipient", "recipient_email"):
                    input_val = clean_text.rstrip(".?").strip()
                    if EmailService.validate_recipient(input_val):
                        recipient = input_val
                        self.pending_context["recipient"] = recipient
                        if not body:
                            self.pending_context["stage"] = "body"
                            logger.info(f"[CommandRouter] Captured email recipient '{recipient}'. Prompting for body.")
                            return "What should the email say?", False, {"intent": "send_email", "confidence": 1.0, "entities": {"email_address": recipient}}
                    else:
                        # Input is a name or unvalidated string
                        self.pending_context["stage"] = "recipient_email"
                        self.pending_context["recipient_name"] = input_val
                        logger.info(f"[CommandRouter] Prompting for email address of recipient '{input_val}'.")
                        return f"What is {input_val}'s email address?", False, {"intent": "send_email", "confidence": 1.0, "entities": {"recipient": input_val}}

                if stage == "body" or (recipient and not body):
                    body = clean_text.rstrip(".?").strip()
                    self.pending_context = None
                    logger.info(f"[CommandRouter] Captured email body. Dispatching email to '{recipient}'.")
                    email_result = EmailService.send_email(recipient, subject, body)
                    response = EmailService.format_email_response(email_result)
                    nlu_res = {
                        "intent": "send_email",
                        "confidence": 1.0,
                        "entities": {"email_address": recipient, "body": body},
                        "raw_text": clean_text
                    }
                    return response, False, nlu_res

        # Step 1: Predict Intent and Extract Entities via NLU Engine
        nlu_result = self.intent_classifier.predict_intent(clean_text)
        intent = nlu_result["intent"]
        confidence = nlu_result["confidence"]
        entities = nlu_result.get("entities", {})

        logger.info(f"NLU Pipeline Result: Input='{clean_text}' -> Intent='{intent}' (Confidence: {confidence:.2f}, Entities: {entities})")

        # Step 2: Handle High-Priority Exit Intent
        if intent == "exit":
            response = f"Goodbye {Config.USER_NAME}! Have a wonderful day."
            return response, True, nlu_result

        # Step 3: Handle Recognized Built-in Intents (Confidence >= Threshold)
        if intent != "unknown" and intent != "empty":
            if intent == "greeting":
                response = DateTimeService.get_greeting()
                return response, False, nlu_result

            elif intent == "get_time":
                response = DateTimeService.get_current_time()
                return response, False, nlu_result

            elif intent == "get_date":
                response = DateTimeService.get_current_date()
                return response, False, nlu_result

            elif intent == "web_search":
                # Prefer extracted entity query, fallback to prefix stripper
                query = entities.get("query") or SearchService.extract_search_query(clean_text)
                response = SearchService.search_web(query)
                return response, False, nlu_result

            elif intent == "get_weather":
                city = entities.get("city")
                if not city:
                    self.pending_context = {"intent": "get_weather"}
                    logger.info("[CommandRouter] Weather intent detected without location. Prompting for city.")
                    return "Which city would you like the weather for?", False, nlu_result

                weather_data = WeatherService.fetch_weather_data(city)
                response = WeatherService.format_weather_response(weather_data)
                return response, False, nlu_result

            elif intent == "knowledge_query":
                query_topic = entities.get("topic") or KnowledgeService.extract_topic(clean_text)
                response = KnowledgeService.get_answer(query_topic)
                return response, False, nlu_result

            elif intent == "send_email":
                email_addr = entities.get("email_address")
                recipient = entities.get("recipient")
                body = entities.get("body")
                subject = entities.get("subject", "Voice Assistant Message")

                # If no email address or recipient name specified
                if not email_addr and not recipient:
                    self.pending_context = {"intent": "send_email", "stage": "recipient", "subject": subject, "body": body}
                    logger.info("[CommandRouter] Email intent detected without recipient. Prompting for recipient.")
                    return "Who should I send it to?", False, nlu_result

                # If recipient is a name and not a valid email address
                if not email_addr or not EmailService.validate_recipient(email_addr):
                    recip_name = recipient or "that person"
                    self.pending_context = {"intent": "send_email", "stage": "recipient_email", "recipient_name": recip_name, "subject": subject, "body": body}
                    logger.info(f"[CommandRouter] Email intent detected with contact name '{recip_name}'. Prompting for email address.")
                    return f"What is {recip_name}'s email address?", False, nlu_result

                # If recipient email address is valid but body is missing
                if not body:
                    self.pending_context = {"intent": "send_email", "stage": "body", "recipient": email_addr, "subject": subject}
                    logger.info(f"[CommandRouter] Email intent detected for '{email_addr}' without body. Prompting for message body.")
                    return "What should the email say?", False, nlu_result

                # All information present -> execute send_email
                email_result = EmailService.send_email(email_addr, subject, body)
                response = EmailService.format_email_response(email_result)
                return response, False, nlu_result

            elif intent == "set_reminder":
                duration_seconds = entities.get("duration_seconds")
                message = entities.get("reminder_message", "Your reminder")

                if not duration_seconds or duration_seconds <= 0:
                    return "Please specify how long from now to set the reminder.", False, nlu_result

                response = ReminderService.set_reminder(duration_seconds, message)
                return response, False, nlu_result

        # Step 4: Check Custom Commands Registry
        matched_custom, custom_response = self.custom_service.match_and_execute(clean_text)
        if matched_custom:
            nlu_result["intent"] = "custom_command"
            return custom_response, False, nlu_result

        # Step 5: Fallback for Unknown / Low Confidence Commands
        fallback_response = "I'm not sure what you mean. Could you please repeat that?"
        return fallback_response, False, nlu_result

from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, Final, List, cast
from typing_extensions import Self
from typing import Final

from viam.resource.types import RESOURCE_NAMESPACE_RDK, RESOURCE_TYPE_SERVICE
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Vector3
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from viam.services.generic import Generic
from viam.logging import getLogger
from viam.utils import ValueTypes, struct_to_dict

import time
import asyncio
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email

LOGGER = getLogger(__name__)

class Preset():
    subject: str
    body: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value
class sendgridEmail(Generic, Reconfigurable):

    MODEL: ClassVar[Model] = Model(ModelFamily("mcvella", "messaging"), "sendgrid-email")
    email_client: SendGridAPIClient
    from_email: str
    from_email_name: str
    preset_messages: dict = {}
    enforce_preset: bool

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        api_key = config.attributes.fields["api_key"].string_value
        if api_key == "":
            raise Exception("An api_key must be defined")
        
        enforce_preset = config.attributes.fields["enforce_preset"].bool_value
        if enforce_preset == True:
            attributes = struct_to_dict(config.attributes)
            preset_messages = attributes.get("preset_messages")
            if preset_messages is None:
                raise Exception("preset_messages must be defined when enforce_preset is set to true")
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        attributes = struct_to_dict(config.attributes)
        preset_messages = attributes.get("preset_messages") or {}
        for p in preset_messages:
            self.preset_messages[p] = Preset(**preset_messages[p])

        self.enforce_preset = config.attributes.fields["enforce_preset"].bool_value or False
        self.from_email = config.attributes.fields["default_from"].string_value or ""
        self.from_email_name = config.attributes.fields["default_from_name"].string_value or ""

        api_key = config.attributes.fields["api_key"].string_value
        self.email_client = SendGridAPIClient(api_key)
        return
    
    async def do_command(
                self,
                command: Mapping[str, ValueTypes],
                *,
                timeout: Optional[float] = None,
                **kwargs
            ) -> Mapping[str, ValueTypes]:
        result = {}

        if 'command' in command:
            if command['command'] == 'send':
                message_args = {}
                if self.enforce_preset and not "preset" in command:
                    return { "error" : "preset message must be specified" }

                if 'preset' in command:
                    message_args['html_content'] = self.preset_messages[command['preset']].body
                    message_args['subject'] = self.preset_messages[command['preset']].subject
                else:
                    message_args['html_content'] = command['body'] or ""
                    message_args['subject'] = command['subject'] or ""
                
                # replace templated params
                if 'template_vars' in command:
                    for key, val in command['template_vars'].items():
                        message_args['html_content'] = message_args['html_content'].replace(f"<<{key}>>", val)
                        message_args['subject'] = message_args['subject'].replace(f"<<{key}>>", val)

                if 'to' in command:
                    message_args['to_emails'] = command['to']
                else:
                    return { "error": "'to' must be defined" }
                
                from_name = self.from_email_name
                if "from_name" in command:
                    from_name = message_args["from_name"]
                
                if "from" in command:
                    if from_name != "":
                        message_args['from_email'] = Email(email=command['from'], name=from_name)
                    else:
                        message_args['from_email'] = command['from']
                else:
                    if from_name != "":
                        message_args['from_email'] = Email(email=self.from_email, name=from_name)
                    else:
                        message_args['from_email'] = self.from_email

                response = self.email_client.send(Mail(**message_args))
                return {"status_code": response.status_code}
    
        return {"error": "command must be defined"}
"""
This file registers the model with the Python SDK.
"""

from viam.services.generic import Generic
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .sendgridEmail import sendgridEmail

Registry.register_resource_creator(Generic.API, sendgridEmail.MODEL, ResourceCreatorRegistration(sendgridEmail.new, sendgridEmail.validate))

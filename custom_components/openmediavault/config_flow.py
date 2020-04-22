"""Config flow to configure OpenMediaVault."""

import logging

import voluptuous as vol
from homeassistant.config_entries import (
    CONN_CLASS_LOCAL_POLL,
    ConfigFlow,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.core import callback

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_DEVICE_NAME,
)
from .omv_api import OpenMediaVaultAPI

_LOGGER = logging.getLogger(__name__)


# ---------------------------
#   configured_instances
# ---------------------------
@callback
def configured_instances(hass):
    """Return a set of configured instances."""
    return set(
        entry.data[CONF_NAME] for entry in hass.config_entries.async_entries(DOMAIN)
    )


# ---------------------------
#   OpenMediaVaultConfigFlow
# ---------------------------
class OpenMediaVaultConfigFlow(ConfigFlow, domain=DOMAIN):
    """OpenMediaVaultConfigFlow class"""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize OpenMediaVaultConfigFlow."""

    async def async_step_import(self, user_input=None):
        """Occurs when a previously entry setup fails and is re-initiated."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            # Check if instance with this name already exists
            if user_input[CONF_NAME] in configured_instances(self.hass):
                errors["base"] = "name_exists"

            # Test connection
            api = OpenMediaVaultAPI(
                host=user_input[CONF_HOST],
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )
            if not api.connect():
                errors[CONF_HOST] = api.error

            # Save instance
            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

            return self._show_config_form(user_input=user_input, errors=errors)

        return self._show_config_form(
            user_input={
                CONF_NAME: DEFAULT_DEVICE_NAME,
                CONF_HOST: DEFAULT_HOST,
                CONF_USERNAME: DEFAULT_USERNAME,
                CONF_PASSWORD: DEFAULT_PASSWORD,
            },
            errors=errors,
        )

    # ---------------------------
    #   _show_config_form
    # ---------------------------
    def _show_config_form(self, user_input, errors=None):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                }
            ),
            errors=errors,
        )
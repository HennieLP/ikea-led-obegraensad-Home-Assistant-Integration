"""Config flow for IKEA OBEGRÄNSAD LED Control integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
import voluptuous as vol

import aiohttp

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow, FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _host_schema(default: str | None = None) -> vol.Schema:
    """Build the host form, prefilled with the current host when reconfiguring."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST, description={"suggested_value": default}): str,
        }
    )


def _normalize_host(host: str) -> str:
    """Accept pasted URLs like 'http://192.168.1.5/' and reduce them to the host."""
    host = host.strip()
    for prefix in ("http://", "https://"):
        if host.lower().startswith(prefix):
            host = host[len(prefix):]
    return host.split("/", 1)[0]


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IKEA OBEGRÄNSAD LED Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = _normalize_host(user_input[CONF_HOST])

            errors = await self._async_validate_host(host)
            if not errors:
                # Check if already configured
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"IKEA OBEGRÄNSAD LED ({host})",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_host_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Change the host of an existing entry, e.g. after the device got a new IP.

        Entities are keyed on the entry id, so they survive the change.
        """
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            host = _normalize_host(user_input[CONF_HOST])

            errors = await self._async_validate_host(host)
            if not errors:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_mismatch_other_entries(entry)
                return self.async_update_reload_and_abort(
                    entry,
                    unique_id=host,
                    title=f"IKEA OBEGRÄNSAD LED ({host})",
                    data_updates={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_host_schema(entry.data.get(CONF_HOST)),
            errors=errors,
        )

    def _abort_if_unique_id_mismatch_other_entries(
        self, entry: config_entries.ConfigEntry
    ) -> None:
        """Abort if another entry already uses the host we are moving to."""
        for other in self._async_current_entries(include_ignore=False):
            if other.entry_id != entry.entry_id and other.unique_id == self.unique_id:
                raise AbortFlow("already_configured")

    async def _async_validate_host(self, host: str) -> dict[str, str]:
        """Return form errors for the host, empty if the device answered."""
        try:
            await _test_connection(self.hass, host)
        except CannotConnect:
            return {"base": "cannot_connect"}
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return {"base": "unknown"}
        return {}


async def _test_connection(hass: HomeAssistant, host: str) -> None:
    """Check the device answers its status endpoint with the expected fields."""
    session = async_get_clientsession(hass)
    try:
        async with asyncio.timeout(10):
            response = await session.get(f"http://{host}/api/info")
            response.raise_for_status()
            data = await response.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError) as ex:
        _LOGGER.warning("Could not reach IKEA LED device at %s: %s", host, ex)
        raise CannotConnect from ex

    if not isinstance(data, dict) or "brightness" not in data:
        _LOGGER.warning("Device at %s returned unexpected data: %s", host, data)
        raise CannotConnect

    _LOGGER.info("Successfully connected to IKEA LED device at %s", host)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

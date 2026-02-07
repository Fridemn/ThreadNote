"""Internationalization helpers using gettext."""

import locale
from gettext import GNUTranslations, translation
from typing import Callable, Optional

from ..config import load_config
from ..constants import APP_NAME, DEFAULT_LOCALE


def resolve_locale(preferred_locale: Optional[str]) -> str:
    """Resolve the locale to use, falling back to defaults."""
    if preferred_locale:
        return preferred_locale
    system_locale, _encoding = locale.getdefaultlocale()
    return system_locale or DEFAULT_LOCALE


def get_translation(preferred_locale: Optional[str] = None) -> GNUTranslations:
    """Return a gettext translation object."""
    config = load_config()
    locale_code = resolve_locale(preferred_locale)
    return translation(
        APP_NAME,
        localedir=str(config.locales_path),
        languages=[locale_code],
        fallback=True,
    )


def gettext_factory(preferred_locale: Optional[str] = None) -> Callable[[str], str]:
    """Return a gettext function for translating strings."""
    return get_translation(preferred_locale).gettext

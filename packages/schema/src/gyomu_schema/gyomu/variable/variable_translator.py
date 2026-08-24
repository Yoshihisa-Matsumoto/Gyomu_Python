from datetime import date
from typing import Protocol

from gyomu_schema.error.database import DatabaseError
from gyomu_schema.error.validation import ValidationError
from returns.result import Result


class VariableTranslator(Protocol):
    """
    Gyomu Context:
      Translates variable expressions embedded in strings.

      A variable expression must be enclosed by ``{%`` and ``%}``::

          {%<expression>%}

      Date variables use the following syntax::

          {%<Market>$<Factor Index>$<Keyword>$<Format>%}

      ``<Market>`` and ``<Factor Index>`` are optional. The following forms
      are therefore also valid::

          {%<Keyword>$<Format>%}
          {%<Market>$<Keyword>$<Format>%}
          {%<Factor Index>$<Keyword>$<Format>%}
          {%<Market>$<Factor Index>$<Keyword>$<Format>%}

      The order of the components is significant.

      In particular, when a Market or Factor Index is specified, the
      Factor Index must appear immediately before the Date Keyword::

          {%JP$2$NEXTBUS$yyyyMMdd%}

      The Factor Index applies to the Date Keyword that immediately follows it.
      It is not a general-purpose argument and cannot appear after the Keyword.

      Examples::

          {%TODAY$yyyyMMdd%}
          {%NEXTDAY$2$yyyyMMdd%}
          {%JP$NEXTBUS$yyyyMMdd%}
          {%JP$2$NEXTBUS$yyyyMMdd%}

      The supported Date Keywords are:

      - ``TODAY``
      - ``BBOM``
      - ``NEXTBBOM``
      - ``BOM``
      - ``BEOM``
      - ``NEXTBEOM``
      - ``PREVBEOM``
      - ``EOM``
      - ``NEXTBUS``
      - ``NEXTDAY``
      - ``PREVBUS``
      - ``PREVDAY``
      - ``EOY``
      - ``BEOY``
      - ``BBOY``
      - ``BOY``

      ``parse()`` replaces all valid variable expressions in the input string.
      For example::

          "Report date: {%TODAY$yyyyMMdd%}"

      becomes::

          "Report date: 20260821"

      ``parse_date()`` accepts the expression without the ``{%`` and ``%}``
      delimiters and returns the corresponding date.
    """

    def parse(
        self,
        input_string: str,
        target_date: date,
        market: str,
    ) -> Result[str, DatabaseError | ValidationError]: ...

    """
    Gyomu Context:
      Translates variable expressions enclosed by ``{%`` and ``%}``
      within the input string.

      Example:
          ``"Date: {%JP$2$NEXTBUS$yyyyMMdd%}"``
    """

    def parse_date(
        self,
        keyword: str,
        target_date: date,
        market: str,
    ) -> Result[date, DatabaseError | ValidationError]: ...

    """
    Gyomu Context:
      Translates a date keyword expression into a date.

      The expression does not include the ``{%`` and ``%}`` delimiters.

      The syntax is::

          <Market>$<Factor Index>$<Keyword>
          <Market>$<Keyword>

      ``<Factor Index>`` must immediately precede ``<Keyword>``.
    """

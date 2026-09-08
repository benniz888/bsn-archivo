"""Unit coverage for the pure helpers in the Phase 1 enumeration code.

Network paths (fetch_cdx, fetch_one) are not exercised here — they are guarded
by on-disk caching and were run for real during Phase 1.
"""

from src.wayback_cdx import (
    _classify_endpoint,
    _compact_ranges,
    _extract_anio,
    _query_string,
    _status_bucket,
)
from src.fetch_samples import raw_wayback_url
from src.fetch_wayback import _tranche_a, _tranche_b, _tranche_c, local_name


class TestClassifyEndpoint:
    def test_lideres(self):
        assert _classify_endpoint("http://bsnpr.com:80/estadisticas/lideres.asp?anio=1986") == "lideres.asp"

    def test_campeonatos_no_query(self):
        assert _classify_endpoint("http://www.bsnpr.com/estadisticas/campeonatos.asp") == "campeonatos.asp"

    def test_does_not_confuse_print_lideres(self):
        assert _classify_endpoint("http://bsnpr.com/estadisticas/print_lideres.asp") == "print_lideres.asp"

    def test_other_script_kept_verbatim(self):
        assert _classify_endpoint("http://bsnpr.com/estadisticas/enciclopedia.asp?id=5") == "enciclopedia.asp"

    def test_non_estadisticas_is_other(self):
        assert _classify_endpoint("http://bsnpr.com/noticias/index.asp") == "other"


class TestExtractAnio:
    def test_present(self):
        assert _extract_anio("http://x/lideres.asp?anio=1957&liga=1") == "1957"

    def test_url_encoded(self):
        assert _extract_anio("http://x/lideres.asp%3Fanio%3D2004") == "2004"

    def test_absent(self):
        assert _extract_anio("http://x/estadisticas/campeonatos.asp") == ""


class TestQueryString:
    def test_empty_trailing_question_mark(self):
        assert _query_string("http://x/lideres.asp?") == ""

    def test_real_query(self):
        assert _query_string("http://x/lideres.asp?anio=1986&liga=1") == "anio=1986&liga=1"


class TestStatusBucket:
    def test_200_wins_over_redirect_and_error(self):
        assert _status_bucket({"302", "404", "200"}) == "200"

    def test_revisit_when_no_200(self):
        assert _status_bucket({"-", "302"}) == "revisit"

    def test_redirect_only(self):
        assert _status_bucket({"302", "301"}) == "redirect-only"

    def test_error_only(self):
        assert _status_bucket({"404", "500"}) == "error-only"

    def test_absent(self):
        assert _status_bucket(set()) == "absent"


class TestCompactRanges:
    def test_contiguous_and_singletons(self):
        assert _compact_ranges([1958, 1959, 1960, 1972]) == "1958–1960, 1972"

    def test_single(self):
        assert _compact_ranges([1986]) == "1986"

    def test_empty(self):
        assert _compact_ranges([]) == "(none)"


class TestRawWaybackUrl:
    def test_id_suffix(self):
        got = raw_wayback_url("20170804230003", "http://www.bsnpr.com/estadisticas/lideres.asp?anio=1986")
        assert got == "https://web.archive.org/web/20170804230003id_/http://www.bsnpr.com/estadisticas/lideres.asp?anio=1986"


def _row(**kw):
    base = {"endpoint": "lideres.asp", "statuscode": "200", "parametrized": "no",
            "timestamp": "20070529091448", "digest": "ABCDEFGH12345"}
    base.update(kw)
    return base


class TestTranches:
    def test_a_is_campeonatos_200_only(self):
        rows = [_row(endpoint="campeonatos.asp"), _row(endpoint="campeonatos.asp", statuscode="302"),
                _row(endpoint="lideres.asp")]
        assert _tranche_a(rows) == [rows[0]]

    def test_b_is_bare_lideres_200(self):
        rows = [_row(), _row(parametrized="yes"), _row(statuscode="404")]
        assert _tranche_b(rows) == [rows[0]]

    def test_c_is_parametrized_lideres_200(self):
        rows = [_row(parametrized="yes"), _row(parametrized="no"),
                _row(parametrized="yes", endpoint="campeonatos.asp")]
        assert _tranche_c(rows) == [rows[0]]

    def test_local_name(self):
        assert local_name(_row(timestamp="20211026051849", digest="DFFYATXZ9999")) == "20211026051849_DFFYATXZ.html"

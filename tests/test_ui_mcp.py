"""Story #190 (S12): `search` and `get` over the component registries through MCP, and llms.txt.

`scripts/ui_mcp.py` is a stdlib stdio JSON-RPC server named `shipquick_ui_mcp` with two read-only tools:
`shipquick_ui_search_components` (ranked, paginated) and `shipquick_ui_get_component` (doc plus contract).
`python3 scripts/ui_mcp.py llms` writes `ui/llms.txt`; `--check` fails when it drifts from the docs."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ui_mcp

SERVER = ROOT / "scripts" / "ui_mcp.py"
SEARCH, GET = "shipquick_ui_search_components", "shipquick_ui_get_component"


def rpc(*msgs):
    """Send newline-delimited JSON-RPC messages to a fresh server; return the parsed replies."""
    out = subprocess.run([sys.executable, str(SERVER)], input="".join(json.dumps(m) + "\n" for m in msgs),
                         capture_output=True, text=True, timeout=60, check=True).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def call(name, args, id_=2):
    return {"jsonrpc": "2.0", "id": id_, "method": "tools/call", "params": {"name": name, "arguments": args}}


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}


def test_s190_the_server_names_itself_and_lists_two_annotated_tools_with_described_inputs():
    init, tools = rpc(INIT, {"jsonrpc": "2.0", "method": "notifications/initialized"},
                      {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert init["result"]["serverInfo"]["name"] == "shipquick_ui_mcp"
    assert "tools" in init["result"]["capabilities"]
    listed = {t["name"]: t for t in tools["result"]["tools"]}
    assert set(listed) == {SEARCH, GET}
    for t in listed.values():
        a = t["annotations"]
        assert a["readOnlyHint"] is True and a["destructiveHint"] is False
        assert a["idempotentHint"] is True and a["openWorldHint"] is False
        assert t["description"]
        for prop in t["inputSchema"]["properties"].values():
            assert prop.get("description"), t["name"]


def test_s190_search_returns_ranked_matches_with_pagination():
    first = ui_mcp.search("button", limit=3)
    assert first["items"][0]["name"] == "Button"          # exact name beats a keyword hit
    scores = [i["score"] for i in first["items"]]
    assert scores == sorted(scores, reverse=True)
    assert first["count"] == 3 and first["total"] > 3 and first["has_more"] is True
    assert first["next_offset"] == 3
    second = ui_mcp.search("button", limit=3, offset=first["next_offset"])
    assert not {i["name"] for i in first["items"]} & {i["name"] for i in second["items"]}
    last = ui_mcp.search("button", limit=50, offset=0)
    assert last["has_more"] is False and last["next_offset"] is None


def test_s190_search_filters_by_platform_and_reports_no_match_plainly():
    assert all("ios" in i["platforms"] for i in ui_mcp.search("button", platform="ios")["items"])
    none = ui_mcp.search("zzqqxx")
    assert none["total"] == 0 and none["items"] == []


def test_s190_get_returns_the_doc_and_the_contract():
    got = ui_mcp.get("button")                             # case does not matter
    assert got["name"] == "Button"
    assert got["doc"]["platforms"]["android"] == "androidx.compose.material3.Button"
    assert got["contract"]["name"] == "Button"
    assert "registry" in got


def test_s190_an_unknown_name_gives_an_actionable_error_over_mcp():
    _, err = rpc(INIT, call(GET, {"name": "Buton"}))
    res = err["result"]
    assert res["isError"] is True
    text = res["content"][0]["text"]
    assert "Buton" in text and "Button" in text and SEARCH in text   # names the miss, a guess, and the next step


def test_s190_search_over_mcp_returns_text_and_structured_content():
    _, res = rpc(INIT, call(SEARCH, {"query": "date picker", "limit": 2}))
    r = res["result"]
    assert not r.get("isError")
    assert r["structuredContent"]["count"] == 2
    assert json.loads(r["content"][0]["text"]) == r["structuredContent"]


def test_s190_bad_input_and_unknown_tool_are_errors_that_name_the_fix():
    _, bad, unknown = rpc(INIT, call(SEARCH, {"query": "", "limit": 500}), call("nope", {}, id_=3))
    assert bad["result"]["isError"] is True and "limit" in bad["result"]["content"][0]["text"]
    assert unknown["error"]["code"] == -32602 and SEARCH in unknown["error"]["message"]


def test_s190_llms_txt_is_current_and_the_check_catches_drift(tmp_path):
    text = ui_mcp.llms_text()
    assert text.startswith("# ") and "\n> " in text and "[Button](components/Button/Button.doc.mjs)" in text
    assert (ROOT / "ui" / "llms.txt").read_text(encoding="utf-8") == text
    ok = subprocess.run([sys.executable, str(SERVER), "llms", "--check"], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    stale = tmp_path / "llms.txt"
    stale.write_text(text + "- [Ghost](x): gone\n", encoding="utf-8")
    bad = subprocess.run([sys.executable, str(SERVER), "llms", "--check", "--out", str(stale)],
                         capture_output=True, text=True)
    assert bad.returncode == 1 and "ui_mcp.py llms" in bad.stdout + bad.stderr


# ---- #414 review: error paths ----

def raw_rpc(text):
    out = subprocess.run([sys.executable, str(SERVER)], input=text, capture_output=True, text=True, timeout=60).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def test_s190_a_punctuation_only_query_matches_nothing():
    assert ui_mcp.search("!!!")["total"] == 0
    assert ui_mcp.search("-")["items"] == []


def test_s190_an_offset_past_the_total_gives_an_empty_last_page():
    r = ui_mcp.search("button", offset=10_000)
    assert r["items"] == [] and r["count"] == 0 and r["has_more"] is False and r["next_offset"] is None


def test_s190_limit_and_offset_out_of_range_are_errors_naming_the_field():
    replies = rpc(INIT, call(SEARCH, {"query": "a", "limit": 0}, 2), call(SEARCH, {"query": "a", "limit": 51}, 3),
                  call(SEARCH, {"query": "a", "offset": -1}, 4))
    for r, field in zip(replies[1:], ("limit", "limit", "offset")):
        assert r["result"]["isError"] is True and field in r["result"]["content"][0]["text"]


def test_s190_a_parse_error_gives_32700_and_the_session_goes_on():
    replies = raw_rpc("not json\n" + json.dumps({"jsonrpc": "2.0", "id": 9, "method": "ping"}) + "\n")
    assert replies[0]["error"]["code"] == -32700 and replies[0]["id"] is None
    assert replies[1] == {"jsonrpc": "2.0", "id": 9, "result": {}}


def test_s190_an_unknown_method_gives_32601_and_as_a_notification_gets_no_reply():
    replies = rpc({"jsonrpc": "2.0", "method": "nope/notify"}, {"jsonrpc": "2.0", "id": 5, "method": "nope"})
    assert len(replies) == 1 and replies[0]["id"] == 5 and replies[0]["error"]["code"] == -32601


def test_s190_a_client_response_gets_no_reply_and_a_non_object_gets_32600():
    replies = raw_rpc(json.dumps({"jsonrpc": "2.0", "id": 7, "result": {}}) + "\n"
                      + json.dumps({"jsonrpc": "2.0", "id": 8, "error": {"code": 1, "message": "x"}}) + "\n"
                      + "[1, 2]\n42\n")
    assert [r["error"]["code"] for r in replies] == [-32600, -32600]
    assert all(r["id"] is None for r in replies)


def test_s190_malformed_params_and_arguments_get_an_error_with_the_id_and_the_session_goes_on():
    replies = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": [1]},
                  {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": "x"},
                  {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": GET, "arguments": 5}},
                  {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": SEARCH, "arguments": [1]}},
                  {"jsonrpc": "2.0", "id": 5, "method": "ping"})
    assert [r["id"] for r in replies] == [1, 2, 3, 4, 5]
    for r in replies[:4]:
        assert r["error"]["code"] == -32602 and "object" in r["error"]["message"]
    assert replies[4]["result"] == {}


def test_s190_a_non_object_registry_row_is_skipped(tmp_path, monkeypatch):
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({"components": ["bad", 3, {"name": "Chipz", "platform": "android", "base": "Chip"}]}))
    monkeypatch.setattr(ui_mcp, "REGISTRY", reg)
    ui_mcp.load.cache_clear()
    try:
        assert ui_mcp.search("chipz")["items"][0]["name"] == "Chipz"
        assert ui_mcp.get("chipz")["registry"][0]["base"] == "Chip"
        assert "Chipz" in ui_mcp.llms_text()
    finally:
        ui_mcp.load.cache_clear()

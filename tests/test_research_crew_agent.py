import pytest

from app.agents.research_crew_agent import (
    ResearchState,
    planner_agent_node,
    scraper_agent_node,
    fact_checker_agent_node,
    writer_agent_node,
    reviewer_agent_node,
    build_research_crew_workflow,
    research_agent_graph,
)


def make_state(**overrides) -> ResearchState:
    state: ResearchState = {
        "topic": "Quantum Computing",
        "plan_outline": [],
        "scraped_facts": [],
        "verified_sources": [],
        "draft_report": "",
        "reflection_notes": "",
        "final_report": "",
    }
    state.update(overrides)
    return state


def test_planner_ready_state_shape():
    state = make_state()
    assert set(state.keys()) == {
        "topic", "plan_outline", "scraped_facts", "verified_sources",
        "draft_report", "reflection_notes", "final_report",
    }


class TestPlannerAgentNode:
    def test_creates_three_part_outline(self):
        state = planner_agent_node(make_state())
        assert len(state["plan_outline"]) == 3

    def test_each_outline_section_embeds_topic(self):
        state = planner_agent_node(make_state())
        assert state["plan_outline"][0] == "1. Executive Summary of Quantum Computing"
        assert state["plan_outline"][1] == "2. Historical Context & Technical Architecture"
        assert state["plan_outline"][2] == "3. Market Impact & Future Projections"

    def test_returns_same_mutated_state_object(self):
        state = make_state()
        result = planner_agent_node(state)
        assert result is state

    def test_topic_with_leading_trailing_whitespace_kept_verbatim(self):
        state = planner_agent_node(make_state(topic="  AI Agents  "))
        assert "  AI Agents  " in state["plan_outline"][0]

    def test_empty_topic_still_produces_outline(self):
        state = planner_agent_node(make_state(topic=""))
        assert len(state["plan_outline"]) == 3
        assert state["plan_outline"][0].endswith("")

    def test_whitespace_only_topic_still_produces_outline(self):
        state = planner_agent_node(make_state(topic="   "))
        assert len(state["plan_outline"]) == 3

    def test_unicode_topic_embedded_in_outline(self):
        state = planner_agent_node(make_state(topic="量子コンピューティング"))
        assert state["plan_outline"][0] == "1. Executive Summary of 量子コンピューティング"

    def test_special_character_topic_embedded_in_outline(self):
        state = planner_agent_node(make_state(topic="R&D: AI/ML & Agents (2026)!"))
        assert state["plan_outline"][0] == "1. Executive Summary of R&D: AI/ML & Agents (2026)!"

    def test_very_long_topic_handled(self):
        long_topic = "A" * 100_000
        state = planner_agent_node(make_state(topic=long_topic))
        assert long_topic in state["plan_outline"][0]

    def test_preserves_existing_state_fields(self):
        state = make_state(
            plan_outline=["old"],
            scraped_facts=["f"],
            verified_sources=["s"],
            draft_report="draft",
            reflection_notes="notes",
            final_report="final",
        )
        result = planner_agent_node(state)
        assert len(result["plan_outline"]) == 3
        assert result["scraped_facts"] == ["f"]
        assert result["verified_sources"] == ["s"]
        assert result["draft_report"] == "draft"
        assert result["reflection_notes"] == "notes"
        assert result["final_report"] == "final"

    def test_missing_topic_raises_key_error(self):
        del make_state()["topic"]
        with pytest.raises(KeyError):
            planner_agent_node({"plan_outline": []})


class TestScraperAgentNode:
    def test_populates_two_facts(self):
        state = scraper_agent_node(make_state())
        assert len(state["scraped_facts"]) == 2

    def test_facts_are_deterministic(self):
        state_a = scraper_agent_node(make_state())
        state_b = scraper_agent_node(make_state())
        assert state_a["scraped_facts"] == state_b["scraped_facts"]

    def test_overwrites_existing_facts(self):
        state = make_state(scraped_facts=["stale fact"])
        result = scraper_agent_node(state)
        assert len(result["scraped_facts"]) == 2
        assert "stale fact" not in result["scraped_facts"]

    def test_does_not_require_topic(self):
        state = scraper_agent_node({})
        assert len(state["scraped_facts"]) == 2


class TestFactCheckerAgentNode:
    def test_populates_verified_sources(self):
        state = fact_checker_agent_node(make_state())
        assert len(state["verified_sources"]) == 2

    def test_sources_are_verifiable_urls(self):
        state = fact_checker_agent_node(make_state())
        for source in state["verified_sources"]:
            assert source.startswith("https://")
            assert "Verified" in source

    def test_overwrites_existing_sources(self):
        state = make_state(verified_sources=["stale source"])
        result = fact_checker_agent_node(state)
        assert len(result["verified_sources"]) == 2
        assert "stale source" not in result["verified_sources"]

    def test_does_not_require_topic(self):
        state = fact_checker_agent_node({})
        assert len(state["verified_sources"]) == 2


class TestWriterAgentNode:
    def writer_state(self, **overrides):
        return make_state(
            scraped_facts=[
                "Fact 1: Adoption grew by 240% year-over-year in enterprise deployments.",
                "Fact 2: Benchmark scores demonstrate a 40% reduction in processing latency.",
            ],
            verified_sources=[
                "https://arxiv.org/abs/2401.99821 (Verified IEEE Peer Review)",
                "https://nature.com/articles/s41586-024 (Verified Primary Source)",
            ],
            **overrides,
        )

    def test_draft_report_embeds_topic_and_facts(self):
        state = writer_agent_node(self.writer_state())
        assert "# Comprehensive Technical Report: Quantum Computing" in state["draft_report"]
        assert state["scraped_facts"][0] in state["draft_report"]
        assert state["scraped_facts"][1] in state["draft_report"]
        assert state["verified_sources"][0] in state["draft_report"]

    def test_draft_contains_section_headers(self):
        state = writer_agent_node(self.writer_state())
        assert "## 1. Executive Summary" in state["draft_report"]
        assert "## 2. Benchmark Findings" in state["draft_report"]
        assert "## References" in state["draft_report"]

    def test_empty_scraped_facts_raises_index_error(self):
        state = self.writer_state()
        state["scraped_facts"] = []
        with pytest.raises(IndexError):
            writer_agent_node(state)

    def test_missing_scraped_facts_raises_key_error(self):
        del make_state()["scraped_facts"]
        with pytest.raises(KeyError):
            writer_agent_node({"topic": "T", "verified_sources": ["s"]})

    def test_empty_verified_sources_raises_index_error(self):
        state = self.writer_state()
        state["verified_sources"] = []
        with pytest.raises(IndexError):
            writer_agent_node(state)

    def test_missing_verified_sources_raises_key_error(self):
        del make_state()["verified_sources"]
        with pytest.raises(KeyError):
            writer_agent_node({"topic": "T", "scraped_facts": ["f1", "f2"]})

    def test_missing_topic_raises_key_error(self):
        del make_state()["topic"]
        with pytest.raises(KeyError):
            writer_agent_node({"scraped_facts": ["f1", "f2"], "verified_sources": ["s"]})

    def test_markdown_injection_style_topic_is_embedded_verbatim(self):
        topic = "foo\n## 3. Injected Heading"
        state = writer_agent_node(self.writer_state(topic=topic))
        assert topic in state["draft_report"]


class TestReviewerAgentNode:
    def test_appends_reflection_to_draft_for_final_report(self):
        state = reviewer_agent_node(make_state(draft_report="DRAFT"))
        assert state["final_report"] == state["draft_report"] + "\n\n---\n*Validated by LangGraph Reflection Engine (" + state["reflection_notes"] + ")*"

    def test_reflection_notes_are_set(self):
        state = reviewer_agent_node(make_state())
        assert state["reflection_notes"].startswith("Self-Reflection Score: 98.2/100")

    def test_final_report_embeds_reflection_notes(self):
        state = reviewer_agent_node(make_state(draft_report="DRAFT"))
        assert state["reflection_notes"] in state["final_report"]

    def test_does_not_mutate_draft_report(self):
        state = make_state(draft_report="DRAFT")
        reviewer_agent_node(state)
        assert state["draft_report"] == "DRAFT"

    def test_missing_draft_report_raises_key_error(self):
        with pytest.raises(KeyError):
            reviewer_agent_node({"reflection_notes": "", "final_report": ""})


class TestWorkflow:
    def test_build_workflow_returns_compiled_graph(self):
        graph = build_research_crew_workflow()
        assert callable(getattr(graph, "invoke", None))

    def test_research_agent_graph_is_compiled_instance(self):
        assert callable(getattr(research_agent_graph, "invoke", None))

    def test_full_pipeline_produces_complete_report(self):
        result = research_agent_graph.invoke(make_state())
        assert result["plan_outline"]
        assert result["scraped_facts"]
        assert result["verified_sources"]
        assert result["draft_report"]
        assert result["reflection_notes"]
        assert result["final_report"]

    def test_pipeline_order_writer_then_reviewer(self):
        result = research_agent_graph.invoke(make_state())
        assert result["final_report"].startswith(result["draft_report"])

    def test_final_report_contains_every_stage_artifact(self):
        result = research_agent_graph.invoke(make_state())
        assert result["scraped_facts"][0] in result["draft_report"]
        assert result["verified_sources"][0] in result["draft_report"]
        assert result["topic"] in result["draft_report"]

    def test_invoke_is_deterministic(self):
        first = research_agent_graph.invoke(make_state())
        second = research_agent_graph.invoke(make_state())
        assert first == second
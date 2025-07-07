"""
LangGraph-based interview orchestration flow
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from ..interviews.schemas import LangGraphState
from .workflow import interview_workflow


class InterviewFlow:
    """LangGraph-based interview flow orchestration."""
    
    def __init__(self):
        self.graph = self._build_interview_graph()
    
    def _build_interview_graph(self) -> StateGraph:
        """Build the LangGraph interview workflow."""
        
        # Define the graph
        workflow = StateGraph(LangGraphState)
        
        # Add all workflow nodes
        workflow.add_node("initialize_session", self._initialize_session_node)
        workflow.add_node("validate_session", self._validate_session_node)
        workflow.add_node("generate_questions", self._generate_questions_node)
        workflow.add_node("check_prerequisites", self._check_prerequisites_node)
        workflow.add_node("present_question", self._present_question_node)
        workflow.add_node("wait_for_response", self._wait_for_response_node)
        workflow.add_node("process_audio", self._process_audio_node)
        workflow.add_node("validate_response", self._validate_response_node)
        workflow.add_node("evaluate_response", self._evaluate_response_node)
        workflow.add_node("analyze_depth", self._analyze_depth_node)
        workflow.add_node("generate_follow_up", self._generate_follow_up_node)
        workflow.add_node("calculate_score", self._calculate_score_node)
        workflow.add_node("generate_feedback", self._generate_feedback_node)
        workflow.add_node("check_termination", self._check_termination_node)
        workflow.add_node("prepare_next_question", self._prepare_next_question_node)
        workflow.add_node("complete_interview", self._complete_interview_node)
        workflow.add_node("generate_insights", self._generate_insights_node)
        workflow.add_node("end_interview", self._end_interview_node)
        
        # Set entry point
        workflow.set_entry_point("initialize_session")
        
        # Define the flow edges
        workflow.add_edge("initialize_session", "validate_session")
        workflow.add_edge("validate_session", "generate_questions")
        workflow.add_edge("generate_questions", "check_prerequisites")
        workflow.add_edge("check_prerequisites", "present_question")
        workflow.add_edge("present_question", "wait_for_response")
        
        # Response processing flow
        workflow.add_conditional_edges(
            "wait_for_response",
            self._route_response_processing,
            {
                "process_audio": "process_audio",
                "validate_response": "validate_response",
                "timeout": "check_termination"
            }
        )
        
        workflow.add_edge("process_audio", "validate_response")
        workflow.add_edge("validate_response", "evaluate_response")
        workflow.add_edge("evaluate_response", "analyze_depth")
        workflow.add_edge("analyze_depth", "generate_follow_up")
        workflow.add_edge("generate_follow_up", "calculate_score")
        workflow.add_edge("calculate_score", "generate_feedback")
        workflow.add_edge("generate_feedback", "check_termination")
        
        # Decision point: continue or complete
        workflow.add_conditional_edges(
            "check_termination",
            self._route_next_step,
            {
                "next_question": "prepare_next_question",
                "complete": "complete_interview",
                "error": "complete_interview"
            }
        )
        
        workflow.add_edge("prepare_next_question", "present_question")
        workflow.add_edge("complete_interview", "generate_insights")
        workflow.add_edge("generate_insights", "end_interview")
        workflow.add_edge("end_interview", END)
        
        return workflow.compile()
    
    # Node implementations
    async def _initialize_session_node(self, state: LangGraphState) -> LangGraphState:
        """Initialize session node."""
        return await interview_workflow.initialize_session(state)
    
    async def _validate_session_node(self, state: LangGraphState) -> LangGraphState:
        """Validate session node."""
        return await interview_workflow.validate_session(state)
    
    async def _generate_questions_node(self, state: LangGraphState) -> LangGraphState:
        """Generate questions node."""
        return await interview_workflow.generate_questions(state)
    
    async def _check_prerequisites_node(self, state: LangGraphState) -> LangGraphState:
        """Check prerequisites node."""
        return await interview_workflow.check_interview_prerequisites(state)
    
    async def _present_question_node(self, state: LangGraphState) -> LangGraphState:
        """Present question node."""
        return await interview_workflow.present_question(state)
    
    async def _wait_for_response_node(self, state: LangGraphState) -> LangGraphState:
        """Wait for user response node."""
        # This node represents waiting for user input
        # In a real implementation, this would be handled by the API
        state.current_step = "waiting_for_response"
        return state
    
    async def _process_audio_node(self, state: LangGraphState) -> LangGraphState:
        """Process audio node."""
        return await interview_workflow.process_audio(state)
    
    async def _validate_response_node(self, state: LangGraphState) -> LangGraphState:
        """Validate response node."""
        return await interview_workflow.validate_response(state)
    
    async def _evaluate_response_node(self, state: LangGraphState) -> LangGraphState:
        """Evaluate response node."""
        return await interview_workflow.evaluate_response(state)
    
    async def _analyze_depth_node(self, state: LangGraphState) -> LangGraphState:
        """Analyze response depth node."""
        return await interview_workflow.analyze_response_depth(state)
    
    async def _generate_follow_up_node(self, state: LangGraphState) -> LangGraphState:
        """Generate follow-up node."""
        return await interview_workflow.generate_dynamic_follow_up(state)
    
    async def _calculate_score_node(self, state: LangGraphState) -> LangGraphState:
        """Calculate score node."""
        return await interview_workflow.calculate_progressive_score(state)
    
    async def _generate_feedback_node(self, state: LangGraphState) -> LangGraphState:
        """Generate feedback node."""
        return await interview_workflow.generate_feedback(state)
    
    async def _check_termination_node(self, state: LangGraphState) -> LangGraphState:
        """Check termination conditions node."""
        return await interview_workflow.check_termination_conditions(state)
    
    async def _prepare_next_question_node(self, state: LangGraphState) -> LangGraphState:
        """Prepare next question node."""
        return await interview_workflow.prepare_next_question(state)
    
    async def _complete_interview_node(self, state: LangGraphState) -> LangGraphState:
        """Complete interview node."""
        return await interview_workflow.complete_interview(state)
    
    async def _generate_insights_node(self, state: LangGraphState) -> LangGraphState:
        """Generate insights node."""
        return await interview_workflow.generate_interview_insights(state)
    
    async def _end_interview_node(self, state: LangGraphState) -> LangGraphState:
        """End interview node."""
        state.current_step = "interview_completed"
        return state
    
    # Routing functions
    def _route_response_processing(self, state: LangGraphState) -> Literal["process_audio", "validate_response", "timeout"]:
        """Route based on response type."""
        if state.error_message and "timeout" in state.error_message.lower():
            return "timeout"
        elif state.audio_data:
            return "process_audio"
        else:
            return "validate_response"
    
    def _route_next_step(self, state: LangGraphState) -> Literal["next_question", "complete", "error"]:
        """Route based on termination conditions."""
        if state.error_message:
            return "error"
        elif state.should_continue:
            return "next_question"
        else:
            return "complete"
    
    # Public interface methods
    async def start_interview(self, initial_state: LangGraphState) -> LangGraphState:
        """Start a new interview session."""
        # Run the graph from initialization to first question
        result = await self.graph.ainvoke(initial_state, {"recursion_limit": 50})
        return result
    
    async def process_response(self, state: LangGraphState, user_response: str, audio_data: bytes = None, audio_format: str = "webm") -> LangGraphState:
        """Process user response and continue interview."""
        # Update state with user input
        state.user_response = user_response
        
        # Handle audio data directly (real-time streaming only)
        if audio_data:
            state.audio_data = audio_data  # Store audio bytes
            state.audio_format = audio_format
        else:
            state.audio_data = None
            state.audio_format = None
        
        # Continue from response processing
        if state.current_step == "waiting_for_response":
            # Resume the graph from response processing
            result = await self._continue_from_response(state)
            return result
        else:
            raise ValueError(f"Invalid state for response processing: {state.current_step}")
    
    async def _continue_from_response(self, state: LangGraphState) -> LangGraphState:
        """Continue graph execution from response processing."""
        # Create a sub-graph for response processing
        response_workflow = StateGraph(LangGraphState)
        
        # Add response processing nodes
        response_workflow.add_node("process_audio", self._process_audio_node)
        response_workflow.add_node("validate_response", self._validate_response_node)
        response_workflow.add_node("evaluate_response", self._evaluate_response_node)
        response_workflow.add_node("analyze_depth", self._analyze_depth_node)
        response_workflow.add_node("generate_follow_up", self._generate_follow_up_node)
        response_workflow.add_node("calculate_score", self._calculate_score_node)
        response_workflow.add_node("generate_feedback", self._generate_feedback_node)
        response_workflow.add_node("check_termination", self._check_termination_node)
        response_workflow.add_node("prepare_next_question", self._prepare_next_question_node)
        response_workflow.add_node("complete_interview", self._complete_interview_node)
        response_workflow.add_node("generate_insights", self._generate_insights_node)
        response_workflow.add_node("end_interview", self._end_interview_node)
        
        # Set entry point based on response type
        if state.audio_data:
            response_workflow.set_entry_point("process_audio")
            response_workflow.add_edge("process_audio", "validate_response")
        else:
            response_workflow.set_entry_point("validate_response")
        
        # Add edges for response processing flow
        response_workflow.add_edge("validate_response", "evaluate_response")
        response_workflow.add_edge("evaluate_response", "analyze_depth")
        response_workflow.add_edge("analyze_depth", "generate_follow_up")
        response_workflow.add_edge("generate_follow_up", "calculate_score")
        response_workflow.add_edge("calculate_score", "generate_feedback")
        response_workflow.add_edge("generate_feedback", "check_termination")
        
        # Decision point
        response_workflow.add_conditional_edges(
            "check_termination",
            self._route_next_step,
            {
                "next_question": "prepare_next_question",
                "complete": "complete_interview",
                "error": "complete_interview"
            }
        )
        
        response_workflow.add_edge("prepare_next_question", END)
        response_workflow.add_edge("complete_interview", "generate_insights")
        response_workflow.add_edge("generate_insights", "end_interview")
        response_workflow.add_edge("end_interview", END)
        
        # Compile and run
        compiled_workflow = response_workflow.compile()
        result = await compiled_workflow.ainvoke(state, {"recursion_limit": 20})
        
        return result
    
    async def get_interview_status(self, state: LangGraphState) -> Dict[str, Any]:
        """Get current interview status."""
        return {
            "current_step": state.current_step,
            "session_token": state.session_token,
            "should_continue": state.should_continue,
            "questions_answered": len(state.responses_history),
            "total_questions": len(state.questions_generated) if state.questions_generated else 0,
            "current_score": getattr(state, 'current_average_score', 0),
            "error_message": state.error_message
        }


# Global interview flow instance
interview_flow = InterviewFlow()

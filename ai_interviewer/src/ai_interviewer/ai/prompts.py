from langchain.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_template("""
            You are an expert interviewer. Generate {number_of_questions} {interview_type} interview question for a {position} position{company_context}.
            
            Requirements:
            - Difficulty level: {difficulty}
            - Interview type: {interview_type}
            - Position: {position}
            - The question should be specific and diverse, covering important aspects for the role
            
            For the question, provide:
            1. The question text
            2. Question type/category
            3. Expected key points candidates should cover
            4. Evaluation criteria with weights (should sum to 1.0)
            
            Return a valid JSON object with this structure:
            {{
              "question": "question text here",
              "type": "question category",
              "difficulty": "{difficulty}",
              "expected_points": ["point1", "point2", "point3"],
              "evaluation_criteria": {{"criteria1": 0.4, "criteria2": 0.6}}
            }}
            
            Question guidelines by type:
            
            TECHNICAL: Focus on programming, system design, algorithms, technologies
            - Easy: Basic concepts, syntax, simple problems
            - Medium: Problem-solving, design patterns, debugging
            - Hard: Complex algorithms, system architecture, optimization
            
            BEHAVIORAL: Focus on past experiences, soft skills, situational judgment
            - Easy: Basic teamwork, communication examples
            - Medium: Leadership, conflict resolution, project management
            - Hard: Complex stakeholder management, strategic decisions
            
            MIXED: Combine technical and behavioral aspects
            
            Make the question specific to the {position} role and avoid generic questions.
            """)

evaluation_prompt = ChatPromptTemplate.from_messages([
  ("system", 
   "You are an expert interviewer and evaluator. You will receive a question, a user's response, "
   "optional expected points, and optional evaluation criteria. Your task is to assess the user's answer. "
   "Return your output strictly as a valid JSON object. Do not include any explanation or text outside the JSON."),
  
  ("human", 
   "Question: {question}\n"
   "User Response: {user_response}\n"
   "{expected_points_section}"
   "{evaluation_criteria_section}"
   "\nEvaluate the user's response based on the question, expected points (if any), and criteria (if any). "
   "Return only a JSON object with:\n"
   "- overall_score (0-10): number\n"
   "- feedback: string\n"
   "- detailed_analysis: object mapping each criterion to a score (0-10)\n"
   "- improvements: list of strings")
])

def render_evalution_prompt(question, user_response, expected_points=None, evaluation_criteria=None):
    expected_points_section = f"Expected Points: {expected_points}\n" if expected_points else ""
    evaluation_criteria_section = f"Evaluation Criteria: {evaluation_criteria}\n" if evaluation_criteria else ""

    return evaluation_prompt.format_messages(
        question=question,
        user_response=user_response,
        expected_points_section=expected_points_section,
        evaluation_criteria_section=evaluation_criteria_section
    )

followup_prompt = ChatPromptTemplate.from_messages([
      ("system", 
       "You are an expert interviewer. You will receive a previous interview question, the user's response, and additional context. "
       "Your task is to generate a follow-up interview question that probes deeper into the user's response. "
       "Return your output strictly as a valid JSON object. Do not include any explanation or text outside the JSON."),
      ("human",
       "Previous Question: {previous_question}\n"
       "User Response: {user_response}\n"
       "Context: {interview_context}\n"
       "Generate a follow-up interview question that probes deeper into the user's response. "
       "Return a JSON object with: question (str), type (str), context (str), reasoning (str).")
    ])    


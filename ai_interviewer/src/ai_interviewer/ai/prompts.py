from langchain.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_template("""
            You are an expert interviewer. Generate {num_questions} {interview_type} interview questions for a {position} position{company_context}.
            
            Requirements:
            - Difficulty level: {difficulty}
            - Interview type: {interview_type}
            - Position: {position}
            - Generate diverse questions covering different aspects
            
            For each question, provide:
            1. The question text
            2. Question type/category
            3. Expected key points candidates should cover
            4. Evaluation criteria with weights (should sum to 1.0)
            
            Return a valid JSON array with this structure:
            [
              {{
                "question": "question text here",
                "type": "question category",
                "difficulty": "{difficulty}",
                "expected_points": ["point1", "point2", "point3"],
                "evaluation_criteria": {{"criteria1": 0.4, "criteria2": 0.6}}
              }}
            ]
            
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
            
            Make questions specific to {position} role and avoid generic questions.
            """)

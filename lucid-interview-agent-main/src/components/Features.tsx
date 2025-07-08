
import { MessageSquare, Brain, FileText, Target } from "lucide-react";

const Features = () => {
  const features = [
    {
      icon: <Brain className="h-8 w-8" />,
      title: "Real-Time Analysis",
      description: "Get instant feedback on your responses, body language, and communication style during the interview."
    },
    {
      icon: <MessageSquare className="h-8 w-8" />,
      title: "Smart Questioning",
      description: "AI adapts questions based on your role, experience level, and interview progress for personalized practice."
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: "Instant Reports",
      description: "Receive detailed performance reports with actionable insights and improvement recommendations."
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: "Skill Targeting",
      description: "Focus on specific competencies and interview types with customized practice scenarios."
    }
  ];

  return (
    <section id="features" className="py-20 bg-dark-bg relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent"></div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-light">
            Why Choose Our <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">AI Agent</span>
          </h2>
          <p className="text-xl text-muted max-w-3xl mx-auto leading-relaxed font-sans">
            Experience the next generation of interview preparation with cutting-edge AI technology 
            that understands your unique needs and helps you succeed.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="group bg-gradient-to-br from-card-bg to-card-bg/80 rounded-2xl p-8 border border-primary/20 hover:border-secondary/40 transition-all duration-300 hover:transform hover:scale-105 backdrop-blur-sm"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="bg-gradient-to-r from-primary to-secondary text-white rounded-xl p-4 w-16 h-16 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-4 text-light group-hover:text-secondary transition-colors duration-300">
                {feature.title}
              </h3>
              <p className="text-muted leading-relaxed group-hover:text-light transition-colors duration-300 font-sans">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;

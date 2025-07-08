
import { Users, MessageSquare, Brain } from "lucide-react";

const HowItWorks = () => {
  const steps = [
    {
      icon: <Users className="h-8 w-8" />,
      title: "Choose Your Role",
      description: "Select the position you're interviewing for and customize your experience with role-specific scenarios."
    },
    {
      icon: <MessageSquare className="h-8 w-8" />,
      title: "Interactive Interview",
      description: "Engage with our advanced AI agent in realistic interview scenarios tailored to your needs."
    },
    {
      icon: <Brain className="h-8 w-8" />,
      title: "Get Insights",
      description: "Receive instant feedback on your performance and personalized recommendations for improvement."
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-gradient-to-br from-dark-bg to-card-bg/20 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-secondary/5 via-transparent to-primary/5"></div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-light">
            How It <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Works</span>
          </h2>
          <p className="text-xl text-muted max-w-3xl mx-auto leading-relaxed font-sans">
            Our AI-powered interview process is designed to give you the most realistic and 
            helpful practice experience possible in just three simple steps.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 relative">
          {steps.map((step, index) => (
            <div key={index} className="relative group">
              <div className="bg-gradient-to-br from-card-bg to-card-bg/80 rounded-2xl p-8 text-center h-full border border-primary/20 hover:border-secondary/40 transition-all duration-300 hover:transform hover:scale-105 backdrop-blur-sm">
                {/* Step number */}
                <div className="absolute -top-4 -left-4 w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold text-sm">
                  {index + 1}
                </div>
                
                <div className="bg-gradient-to-r from-primary to-secondary text-white rounded-xl p-4 w-16 h-16 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  {step.icon}
                </div>
                <h3 className="text-xl font-semibold mb-4 text-light group-hover:text-secondary transition-colors duration-300">
                  {step.title}
                </h3>
                <p className="text-muted leading-relaxed group-hover:text-light transition-colors duration-300 font-sans">
                  {step.description}
                </p>
              </div>
              
              {/* Connection line */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                  <div className="w-8 h-0.5 bg-gradient-to-r from-primary to-secondary opacity-60"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;


import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Users, Trophy, Clock } from "lucide-react";

const Hero = () => {
  return (
    <section className="min-h-screen bg-dark-bg pt-20 pb-16 relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse-slow"></div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center min-h-[80vh]">
          <div className="space-y-6 animate-fade-in-up">
            <div className="space-y-4">
              <div className="inline-flex items-center px-4 py-2 bg-primary/20 text-primary rounded-full text-sm font-medium border border-primary/30">
                ✨ AI-Powered Interview Revolution
              </div>
              <h1 className="text-5xl lg:text-7xl font-lovable font-bold leading-tight text-light">
                Master Your
                <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent block">
                  Next Interview
                </span>
              </h1>
              <p className="text-xl text-muted leading-relaxed max-w-lg font-sans" style={{ lineHeight: '1.5' }}>
                Practice with our intelligent AI agent that provides real-time analysis, adaptive questioning, 
                and instant feedback to transform your interview performance.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <Button 
                size="lg" 
                className="bg-primary hover:bg-primary/90 text-white px-8 py-4 text-lg font-semibold transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-primary/25"
              >
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-2 border-secondary/50 text-secondary hover:bg-secondary/10 px-8 py-4 text-lg bg-transparent transition-all duration-300 hover:scale-105 hover:border-secondary group"
              >
                <Play className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
                Watch Demo
              </Button>
            </div>
            
            <div className="grid grid-cols-3 gap-6 pt-6">
              <div className="bg-gradient-to-br from-card-bg/50 to-card-bg/30 backdrop-blur-sm rounded-xl p-4 text-center border border-primary/10 hover:border-primary/20 transition-all duration-300">
                <div className="flex items-center justify-center mb-2">
                  <Users className="h-5 w-5 text-primary mr-2" />
                  <div className="text-3xl font-bold text-light">10K+</div>
                </div>
                <div className="text-sm text-muted">Interviews Completed</div>
              </div>
              <div className="bg-gradient-to-br from-card-bg/50 to-card-bg/30 backdrop-blur-sm rounded-xl p-4 text-center border border-secondary/10 hover:border-secondary/20 transition-all duration-300">
                <div className="flex items-center justify-center mb-2">
                  <Trophy className="h-5 w-5 text-secondary mr-2" />
                  <div className="text-3xl font-bold text-light">95%</div>
                </div>
                <div className="text-sm text-muted">Success Rate</div>
              </div>
              <div className="bg-gradient-to-br from-card-bg/50 to-card-bg/30 backdrop-blur-sm rounded-xl p-4 text-center border border-primary/10 hover:border-primary/20 transition-all duration-300">
                <div className="flex items-center justify-center mb-2">
                  <Clock className="h-5 w-5 text-primary mr-2" />
                  <div className="text-3xl font-bold text-light">24/7</div>
                </div>
                <div className="text-sm text-muted">AI Available</div>
              </div>
            </div>
          </div>
          
          {/* 3D AI Agent Visual */}
          <div className="relative animate-slide-in-left">
            <div className="relative bg-gradient-to-br from-card-bg/80 to-card-bg/60 backdrop-blur-md rounded-3xl p-8 border border-primary/20 shadow-2xl">
              <div className="aspect-square bg-gradient-to-br from-primary/20 to-secondary/20 rounded-2xl flex items-center justify-center relative overflow-hidden">
                {/* Animated ring behind AI */}
                <div className="absolute inset-0 rounded-2xl">
                  <div className="absolute inset-4 border-2 border-primary/30 rounded-2xl animate-pulse"></div>
                  <div className="absolute inset-8 border border-secondary/40 rounded-2xl animate-pulse" style={{ animationDelay: '1s' }}></div>
                </div>
                
                {/* 3D AI Agent representation */}
                <div className="relative z-10 text-center space-y-6">
                  <div className="w-32 h-32 bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center mx-auto animate-float shadow-2xl relative">
                    <div className="text-white text-4xl font-bold">AI</div>
                    <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-full blur-xl animate-pulse"></div>
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-2xl font-semibold text-light">Your AI Interviewer</h3>
                    <p className="text-muted">Advanced Agent Technology</p>
                  </div>
                </div>
                
                {/* Background grid pattern */}
                <div className="absolute inset-0 opacity-10">
                  <div className="w-full h-full" style={{
                    backgroundImage: `linear-gradient(rgba(99, 102, 241, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(99, 102, 241, 0.3) 1px, transparent 1px)`,
                    backgroundSize: '20px 20px'
                  }}></div>
                </div>
              </div>
            </div>
            
            {/* Enhanced floating badges with icons */}
            <div className="absolute -top-4 -left-4 bg-gradient-to-r from-secondary to-primary text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-xl animate-float flex items-center space-x-2">
              <span>⚡</span>
              <span>Live Feedback</span>
            </div>
            <div className="absolute -bottom-4 -right-4 bg-gradient-to-r from-primary to-secondary text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-xl animate-float flex items-center space-x-2" style={{ animationDelay: '1.5s' }}>
              <span>📊</span>
              <span>Instant Reports</span>
            </div>
            <div className="absolute top-1/2 -right-8 bg-gradient-to-r from-secondary/90 to-primary/90 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow-lg animate-float flex items-center space-x-1" style={{ animationDelay: '0.5s' }}>
              <span>🧠</span>
              <span>Smart Questions</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;

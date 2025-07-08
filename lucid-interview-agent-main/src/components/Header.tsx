
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SignIn from "./SignIn";

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 bg-dark-bg/90 backdrop-blur-md border-b border-primary/20 transition-all duration-300 ${
      isScrolled ? 'shadow-lg border-primary/30' : ''
    }`}>
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center animate-glow">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <span className="text-2xl font-lovable font-semibold text-white">
              InterviewAI
            </span>
          </div>
          
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-muted hover:text-secondary transition-colors duration-300 font-semibold relative group">
              Features
              <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-secondary scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
            </a>
            <a href="#how-it-works" className="text-muted hover:text-secondary transition-colors duration-300 font-semibold relative group">
              How It Works
              <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-secondary scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
            </a>
            <a href="#testimonials" className="text-muted hover:text-secondary transition-colors duration-300 font-semibold relative group">
              Testimonials
              <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-secondary scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
            </a>
          </nav>
          
          <div className="flex items-center space-x-4">
            <SignIn>
              <Button variant="ghost" className="text-muted hover:text-white hover:bg-primary/10 transition-all duration-300 font-semibold">
                Sign In
              </Button>
            </SignIn>
            <Button 
              onClick={() => navigate('/dashboard')}
              className="bg-primary hover:bg-primary/90 text-white font-semibold transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              Dashboard
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

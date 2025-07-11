
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle } from "lucide-react";

interface CTAProps {
  onCtaClick?: () => void;
}

const CTA = ({ onCtaClick }: CTAProps) => {
  return (
    <section className="py-20 bg-gradient-to-br from-primary/10 via-dark-bg to-secondary/10 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-transparent to-secondary/20"></div>
      
      <div className="container mx-auto px-6 text-center relative z-10">
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in-up">
          <h2 className="text-4xl lg:text-6xl font-lovable font-bold leading-tight text-light">
            Ready to Transform Your
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent block">
              Interview Skills?
            </span>
          </h2>
          <p className="text-xl text-muted leading-relaxed max-w-2xl mx-auto font-sans">
            Don't let interview anxiety hold you back. Join thousands of professionals who have 
            already mastered their interviews with our AI-powered platform.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg"
              onClick={onCtaClick}
              className="bg-primary hover:bg-primary/90 text-white px-8 py-4 text-lg font-semibold"
            >
              Start Your Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-2 border-secondary/50 text-secondary hover:bg-secondary/10 px-8 py-4 text-lg bg-transparent"
            >
              Schedule Demo
            </Button>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-8 pt-8">
            <div className="flex items-center space-x-2 text-muted">
              <CheckCircle className="h-5 w-5 text-secondary" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center space-x-2 text-muted">
              <CheckCircle className="h-5 w-5 text-secondary" />
              <span>7-day free trial</span>
            </div>
            <div className="flex items-center space-x-2 text-muted">
              <CheckCircle className="h-5 w-5 text-secondary" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;

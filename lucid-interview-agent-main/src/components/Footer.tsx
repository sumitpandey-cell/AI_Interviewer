
const Footer = () => {
  return (
    <footer className="bg-card-bg border-t border-primary/20">
      <div className="container mx-auto px-6 py-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-card-bg font-bold text-lg">AI</span>
              </div>
              <span className="text-2xl font-lovable font-semibold text-white">InterviewAI</span>
            </div>
            <p className="text-muted max-w-sm">
              Revolutionizing interview preparation with AI-powered agents and real-time feedback.
            </p>
            <div className="flex space-x-4">
              <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center hover:bg-primary/30 cursor-pointer transition-colors">
                <span className="text-primary text-sm">f</span>
              </div>
              <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center hover:bg-primary/30 cursor-pointer transition-colors">
                <span className="text-primary text-sm">t</span>
              </div>
              <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center hover:bg-primary/30 cursor-pointer transition-colors">
                <span className="text-primary text-sm">in</span>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-white">Product</h3>
            <ul className="space-y-2">
              <li><a href="#features" className="text-muted hover:text-secondary transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="text-muted hover:text-secondary transition-colors">How It Works</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Pricing</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">API</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-white">Company</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">About Us</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Blog</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Careers</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Press</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-white">Support</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Help Center</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Contact Us</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="text-muted hover:text-secondary transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-primary/20 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-muted text-center md:text-left">
            &copy; 2024 InterviewAI. All rights reserved. Built with ❤️ for your success.
          </p>
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <span className="text-muted">Made with</span>
            <span className="font-lovable text-secondary">Lovable</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

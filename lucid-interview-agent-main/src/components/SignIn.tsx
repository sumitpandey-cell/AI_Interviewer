
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";

interface SignInProps {
  children: React.ReactNode;
}

const SignIn = ({ children }: SignInProps) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loginData, setLoginData] = useState({ email: "", password: "" });
  const [signupData, setSignupData] = useState({ 
    name: "", 
    email: "", 
    password: "", 
    confirmPassword: "" 
  });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login attempt:", loginData);
    // Add your login logic here
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    if (signupData.password !== signupData.confirmPassword) {
      console.error("Passwords don't match");
      return;
    }
    console.log("Signup attempt:", signupData);
    // Add your signup logic here
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md bg-card-bg border border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl font-lovable text-center text-white">
            Welcome to InterviewAI
          </DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-dark-bg/50">
            <TabsTrigger 
              value="login" 
              className="data-[state=active]:bg-primary data-[state=active]:text-white"
            >
              Sign In
            </TabsTrigger>
            <TabsTrigger 
              value="signup"
              className="data-[state=active]:bg-primary data-[state=active]:text-white"
            >
              Sign Up
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="login" className="space-y-4 mt-6">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-email" className="text-light">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted w-4 h-4" />
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="Enter your email"
                    value={loginData.email}
                    onChange={(e) => setLoginData(prev => ({ ...prev, email: e.target.value }))}
                    className="pl-10 bg-dark-bg/50 border-primary/20 text-white placeholder:text-muted focus:border-primary"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="login-password" className="text-light">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted w-4 h-4" />
                  <Input
                    id="login-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={loginData.password}
                    onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10 bg-dark-bg/50 border-primary/20 text-white placeholder:text-muted focus:border-primary"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted hover:text-light transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center space-x-2 text-muted">
                  <input type="checkbox" className="rounded border-primary/20" />
                  <span>Remember me</span>
                </label>
                <a href="#" className="text-secondary hover:text-secondary/80 transition-colors">
                  Forgot password?
                </a>
              </div>
              
              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-primary/90 text-white font-semibold transition-all duration-300 hover:scale-105 hover:shadow-lg"
              >
                Sign In
              </Button>
            </form>
          </TabsContent>
          
          <TabsContent value="signup" className="space-y-4 mt-6">
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="signup-name" className="text-light">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted w-4 h-4" />
                  <Input
                    id="signup-name"
                    type="text"
                    placeholder="Enter your full name"
                    value={signupData.name}
                    onChange={(e) => setSignupData(prev => ({ ...prev, name: e.target.value }))}
                    className="pl-10 bg-dark-bg/50 border-primary/20 text-white placeholder:text-muted focus:border-primary"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="signup-email" className="text-light">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted w-4 h-4" />
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="Enter your email"
                    value={signupData.email}
                    onChange={(e) => setSignupData(prev => ({ ...prev, email: e.target.value }))}
                    className="pl-10 bg-dark-bg/50 border-primary/20 text-white placeholder:text-muted focus:border-primary"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="signup-password" className="text-light">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted w-4 h-4" />
                  <Input
                    id="signup-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a password"
                    value={signupData.password}
                    onChange={(e) => setSignupData(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10 bg-dark-bg/50 border-primary/20 text-white placeholder:text-muted focus:border-primary"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted hover:text-light transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="signup-confirm" className="text-light">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted w-4 h-4" />
                  <Input
                    id="signup-confirm"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your password"
                    value={signupData.confirmPassword}
                    onChange={(e) => setSignupData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className="pl-10 pr-10 bg-dark-bg/50 border-primary/20 text-white placeholder:text-muted focus:border-primary"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted hover:text-light transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div className="text-sm">
                <label className="flex items-start space-x-2 text-muted">
                  <input type="checkbox" className="rounded border-primary/20 mt-0.5" required />
                  <span>
                    I agree to the{" "}
                    <a href="#" className="text-secondary hover:text-secondary/80 transition-colors">
                      Terms of Service
                    </a>{" "}
                    and{" "}
                    <a href="#" className="text-secondary hover:text-secondary/80 transition-colors">
                      Privacy Policy
                    </a>
                  </span>
                </label>
              </div>
              
              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-primary/90 text-white font-semibold transition-all duration-300 hover:scale-105 hover:shadow-lg"
              >
                Create Account
              </Button>
            </form>
          </TabsContent>
        </Tabs>
        
        <div className="text-center pt-4 border-t border-primary/20">
          <p className="text-sm text-muted">
            Or continue with
          </p>
          <div className="flex justify-center space-x-4 mt-3">
            <Button variant="outline" className="flex-1 border-primary/20 text-muted hover:text-white hover:bg-primary/10">
              Google
            </Button>
            <Button variant="outline" className="flex-1 border-primary/20 text-muted hover:text-white hover:bg-primary/10">
              GitHub
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SignIn;

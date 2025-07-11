
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import Testimonials from "@/components/Testimonials";
import CTA from "@/components/CTA";
import Footer from "@/components/Footer";
import { LoginForm, RegisterForm } from "@/components/auth/AuthForms";
import { AuthAPI } from "@/lib/api";

const Index = () => {
  const [showAuthForm, setShowAuthForm] = useState(false);
  const [isRegisterForm, setIsRegisterForm] = useState(false);
  const navigate = useNavigate();
  
  useEffect(() => {
    // Check if user is already authenticated
    if (AuthAPI.isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const toggleAuthForm = () => {
    setShowAuthForm(!showAuthForm);
  };

  const toggleFormType = () => {
    setIsRegisterForm(!isRegisterForm);
  };

  return (
    <div className="min-h-screen bg-dark-bg">
      <Header onLoginClick={toggleAuthForm} />
      {showAuthForm ? (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/70 backdrop-blur-sm p-4">
          <div className="absolute inset-0" onClick={toggleAuthForm}></div>
          <div className="z-10">
            {isRegisterForm ? (
              <RegisterForm onToggleForm={toggleFormType} />
            ) : (
              <LoginForm onToggleForm={toggleFormType} />
            )}
          </div>
        </div>
      ) : (
        <>
          <Hero onGetStartedClick={() => {
            setShowAuthForm(true);
            setIsRegisterForm(true);
          }} />
          <Features />
          <HowItWorks />
          <Testimonials />
          <CTA onCtaClick={() => {
            setShowAuthForm(true);
            setIsRegisterForm(true);
          }} />
          <Footer />
        </>
      )}
    </div>
  );
};

export default Index;

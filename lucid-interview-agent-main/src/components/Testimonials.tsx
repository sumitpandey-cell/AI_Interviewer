
const Testimonials = () => {
  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Software Engineer",
      company: "Google",
      avatar: "SC",
      text: "The AI interview agent helped me prepare for my Google interview. The experience was incredibly realistic and the feedback was spot-on! I felt so much more confident going into the real interview."
    },
    {
      name: "Michael Rodriguez",
      role: "Product Manager",
      company: "Microsoft",
      avatar: "MR",
      text: "I was nervous about behavioral interviews, but this platform gave me the confidence I needed. The real-time analysis helped me improve my storytelling. Landed my dream job at Microsoft!"
    },
    {
      name: "Emily Johnson",
      role: "Data Scientist",
      company: "Netflix",
      avatar: "EJ",
      text: "The AI feedback on my technical explanations was incredibly detailed. It's like having a personal interview coach available 24/7. The progress tracking feature is amazing too."
    }
  ];

  return (
    <section id="testimonials" className="py-20 bg-dark-bg relative">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-secondary/5"></div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-light">
            What Our <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Users Say</span>
          </h2>
          <p className="text-xl text-muted max-w-3xl mx-auto leading-relaxed font-sans">
            Join thousands of professionals who have transformed their interview skills and 
            landed their dream jobs with our AI-powered platform.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index} 
              className="bg-gradient-to-br from-card-bg to-card-bg/80 rounded-2xl p-8 border border-primary/20 hover:border-secondary/40 transition-all duration-300 hover:transform hover:scale-105 backdrop-blur-sm group"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center text-white font-semibold mr-4">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold text-light group-hover:text-secondary transition-colors duration-300">
                    {testimonial.name}
                  </div>
                  <div className="text-sm text-muted">{testimonial.role}</div>
                  <div className="text-sm font-medium text-primary">{testimonial.company}</div>
                </div>
              </div>
              
              <p className="text-muted leading-relaxed italic group-hover:text-light transition-colors duration-300 font-sans">
                "{testimonial.text}"
              </p>
              
              {/* Star rating */}
              <div className="flex mt-4 space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="w-4 h-4 bg-gradient-to-r from-primary to-secondary rounded-full"></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;

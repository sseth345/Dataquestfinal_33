import { ArrowRight, Shield, Zap, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import heroBg from '@/assets/hero-bg.jpg';

const Hero = () => {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <img 
          src={heroBg} 
          alt="Cybersecurity background"
          className="w-full h-full object-cover opacity-20"
        />
        <div className="absolute inset-0 bg-gradient-hero" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 text-center animate-fade-in">
        <div className="max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-secondary/20 backdrop-blur-md border border-cyber-blue/30 rounded-full px-4 py-2 mb-8">
            <Shield className="h-5 w-5 text-cyber-blue" />
            <span className="text-sm text-foreground">Advanced Threat Detection</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              Protect Your Digital
            </span>
            <br />
            <span className="text-foreground">World</span>
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Advanced AI-powered threat detection that identifies and neutralizes cyber attacks 
            in real-time, keeping your systems and data safe from evolving digital threats.
          </p>

          {/* Feature highlights */}
          <div className="flex flex-wrap justify-center gap-6 mb-10">
            <div className="flex items-center space-x-2 text-cyber-blue">
              <Zap className="h-5 w-5" />
              <span className="text-sm font-medium">Real-time Detection</span>
            </div>
            <div className="flex items-center space-x-2 text-cyber-cyan">
              <Lock className="h-5 w-5" />
              <span className="text-sm font-medium">Advanced Encryption</span>
            </div>
            <div className="flex items-center space-x-2 text-cyber-blue">
              <Shield className="h-5 w-5" />
              <span className="text-sm font-medium">24/7 Protection</span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              className="bg-gradient-primary hover:shadow-glow transition-all duration-300 transform hover:scale-105"
              onClick={() => scrollToSection('download')}
            >
              Download App
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-cyber-blue/50 text-cyber-blue hover:bg-cyber-blue/10"
              onClick={() => scrollToSection('demo')}
            >
              Watch Demo
            </Button>
          </div>
        </div>
      </div>

      {/* Animated elements */}
      <div className="absolute top-1/4 left-10 w-2 h-2 bg-cyber-blue rounded-full animate-ping opacity-50" />
      <div className="absolute top-1/3 right-16 w-3 h-3 bg-cyber-cyan rounded-full animate-ping opacity-30" style={{animationDelay: '1s'}} />
      <div className="absolute bottom-1/4 left-1/4 w-1 h-1 bg-cyber-blue rounded-full animate-ping opacity-40" style={{animationDelay: '2s'}} />
    </section>
  );
};

export default Hero;
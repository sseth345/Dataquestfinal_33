import { useState, useEffect } from 'react';
import { Shield, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

import logo from '@/assets/logo.png';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('hero');

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
      
      // Update active section based on scroll position
      const sections = ['hero', 'about', 'demo', 'gallery', 'contact', 'download'];
      const currentSection = sections.find(section => {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          return rect.top <= 100 && rect.bottom >= 100;
        }
        return false;
      });
      
      if (currentSection) {
        setActiveSection(currentSection);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setIsOpen(false);
    }
  };

  const navItems = [
    { label: 'About', id: 'about' },
    { label: 'Demo Video', id: 'demo' },
    { label: 'Gallery', id: 'gallery' },
    { label: 'Contact', id: 'contact' },
    { label: 'Download App', id: 'download' },
  ];

  return (
    <div>
      {/* Custom Styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes glowPulse {
            0%, 100% { 
              text-shadow: 0 0 5px rgba(59, 130, 246, 0.5), 0 0 10px rgba(59, 130, 246, 0.3); 
              transform: scale(1);
            }
            50% { 
              text-shadow: 0 0 10px rgba(59, 130, 246, 0.8), 0 0 20px rgba(59, 130, 246, 0.5); 
              transform: scale(1.05);
            }
          }
          
          @keyframes slideInFromTop {
            0% { transform: translateY(-100%); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
          }
          
          @keyframes fadeInUp {
            0% { transform: translateY(20px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
          }
          
          @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
          }
          
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
          }

          .animate-glow-pulse {
            animation: glowPulse 3s ease-in-out infinite;
          }
          
          .animate-slide-in {
            animation: slideInFromTop 0.6s ease-out forwards;
          }
          
          .animate-fade-in-up {
            animation: fadeInUp 0.3s ease-out forwards;
          }
          
          .animate-shimmer {
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent);
            background-size: 200% 100%;
            animation: shimmer 2s infinite;
          }
          
          .animate-float {
            animation: float 3s ease-in-out infinite;
          }
          
          .nav-item {
            position: relative;
            overflow: hidden;
          }
          
          .nav-item::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: linear-gradient(90deg, #3b82f6, #06b6d4);
            transition: width 0.3s ease-in-out;
          }
          
          .nav-item:hover::before,
          .nav-item.active::before {
            width: 100%;
          }
          
          .nav-item::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
            transition: left 0.5s ease-in-out;
          }
          
          .nav-item:hover::after {
            left: 100%;
          }
          
          .mobile-item {
            position: relative;
            overflow: hidden;
          }
          
          .mobile-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 3px;
            height: 0;
            background: linear-gradient(180deg, #3b82f6, #06b6d4);
            transition: height 0.3s ease-in-out;
          }
          
          .mobile-item:hover::before,
          .mobile-item.active::before {
            height: 100%;
          }
          
          .glass-effect {
            backdrop-filter: blur(20px);
            background: rgba(15, 23, 42, 0.85);
            border-bottom: 1px solid rgba(59, 130, 246, 0.2);
          }
          
          .logo-glow {
            filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.3));
            transition: filter 0.3s ease;
          }
          
          .logo-glow:hover {
            filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6));
          }
        `
      }} />

      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-out ${
        scrolled ? 'glass-effect shadow-2xl' : 'bg-transparent'
      } animate-slide-in`}>
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Enhanced Logo */}
            <div 
              className="flex items-center space-x-2 cursor-pointer group animate-float" 
              onClick={() => scrollToSection('hero')}
            >
              <div className="relative logo-glow">
<img 
  src={logo}   // public folder me rakho
  alt="App Logo" 
  className="h-8 w-8 object-contain 
             transition-all duration-300 
             group-hover:rotate-12 group-hover:scale-110 
             drop-shadow-[0_0_12px_rgba(59,130,246,0.7)] 
             animate-pulse" 
/>

                <div className="absolute inset-0 bg-blue-400 opacity-20 blur-xl rounded-full group-hover:opacity-40 transition-opacity duration-300"></div>
              </div>
              <span className="text-xl font-bold text-white bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-600 bg-clip-text hover:text-transparent animate-shimmer group-hover:tracking-wider transition-all duration-300">
                ThreatShield
              </span>
            </div>

            {/* Enhanced Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item, index) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={`nav-item px-4 py-2 text-sm font-medium transition-all duration-300 rounded-lg hover:bg-blue-500/10 hover:text-blue-400 hover:scale-105 hover:-translate-y-1 ${
                    activeSection === item.id 
                      ? 'active text-blue-400 bg-blue-500/20' 
                      : 'text-gray-300 hover:text-blue-400'
                  }`}
                  style={{
                    animationDelay: `${index * 0.1}s`
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {/* Enhanced Mobile Menu Button */}
            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(!isOpen)}
                className="text-gray-300 hover:text-blue-400 hover:bg-blue-500/10 transition-all duration-300 hover:scale-110 relative group"
              >
                <div className="absolute inset-0 bg-blue-400/20 rounded-lg scale-0 group-hover:scale-100 transition-transform duration-300"></div>
                <div className="relative">
                  {isOpen ? (
                    <X className="h-6 w-6 rotate-0 transition-transform duration-300 group-hover:rotate-90" />
                  ) : (
                    <Menu className="h-6 w-6 transition-transform duration-300 group-hover:rotate-180" />
                  )}
                </div>
              </Button>
            </div>
          </div>

          {/* Enhanced Mobile Navigation */}
          <div className={`md:hidden overflow-hidden transition-all duration-500 ease-out ${
            isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
          }`}>
            <div className="glass-effect border-t border-blue-500/20 animate-fade-in-up">
              <div className="px-2 pt-2 pb-3 space-y-1">
                {navItems.map((item, index) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className={`mobile-item block w-full text-left px-4 py-3 text-sm font-medium rounded-lg transition-all duration-300 hover:bg-blue-500/10 hover:text-blue-400 hover:translate-x-2 hover:scale-105 ${
                      activeSection === item.id 
                        ? 'active text-blue-400 bg-blue-500/20' 
                        : 'text-gray-300'
                    }`}
                    style={{
                      animationDelay: `${index * 0.1}s`
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full transition-all duration-300 ${
                        activeSection === item.id ? 'bg-blue-400 shadow-lg shadow-blue-400/50' : 'bg-gray-600'
                      }`}></div>
                      <span>{item.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Animated Border */}
        <div className={`absolute bottom-0 left-0 h-px bg-gradient-to-r from-transparent via-blue-400 to-transparent transition-opacity duration-500 ${
          scrolled ? 'opacity-100' : 'opacity-0'
        }`} style={{ width: '100%' }}>        </div>
      </nav>
    </div>
  );
};

export default Navbar;
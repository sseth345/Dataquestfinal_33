import { Shield, Twitter, Linkedin, Github, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    { icon: Twitter, href: '#', label: 'Twitter' },
    { icon: Linkedin, href: '#', label: 'LinkedIn' },
    { icon: Github, href: '#', label: 'GitHub' },
    { icon: Mail, href: '#', label: 'Email' }
  ];

  const quickLinks = [
    { label: 'About Us', href: '#about' },
    { label: 'Features', href: '#about' },
    { label: 'Pricing', href: '#' },
    { label: 'Documentation', href: '#' },
    { label: 'API Reference', href: '#' },
    { label: 'Support', href: '#contact' }
  ];

  const legalLinks = [
    { label: 'Privacy Policy', href: '#' },
    { label: 'Terms of Service', href: '#' },
    { label: 'Security Policy', href: '#' },
    { label: 'Cookie Policy', href: '#' },
    { label: 'Compliance', href: '#' },
    { label: 'GDPR', href: '#' }
  ];

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId.replace('#', ''));
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-background border-t border-border/50">
      <div className="container mx-auto px-4 py-16">
        <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-8">
          {/* Company Info */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-2 mb-6">
              <Shield className="h-8 w-8 text-cyber-blue animate-glow-pulse" />
              <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                ThreatShield
              </span>
            </div>
            <p className="text-muted-foreground mb-6 leading-relaxed">
              Advanced AI-powered cybersecurity solutions protecting organizations worldwide 
              from evolving digital threats with real-time detection and response.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-3 text-muted-foreground">
                <MapPin className="h-4 w-4 text-cyber-blue" />
                <span>VIT Chennai</span>
              </div>
              <div className="flex items-center space-x-3 text-muted-foreground">
                <Phone className="h-4 w-4 text-cyber-cyan" />
                <span>+91 7903632892</span>
              </div>
              <div className="flex items-center space-x-3 text-muted-foreground">
                <Mail className="h-4 w-4 text-cyber-blue" />
                <span>shreyashgautam2007@gmail.com</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold text-foreground mb-6">Quick Links</h3>
            <ul className="space-y-3">
              {quickLinks.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => scrollToSection(link.href)}
                    className="text-muted-foreground hover:text-cyber-blue transition-colors duration-300 text-sm"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-lg font-semibold text-foreground mb-6">Legal</h3>
            <ul className="space-y-3">
              {legalLinks.map((link, index) => (
                <li key={index}>
                  <a
                    href={link.href}
                    className="text-muted-foreground hover:text-cyber-blue transition-colors duration-300 text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter & Social */}
          <div>
            <h3 className="text-lg font-semibold text-foreground mb-6">Stay Connected</h3>
            <p className="text-muted-foreground text-sm mb-4">
              Get the latest security insights and threat intelligence delivered to your inbox.
            </p>
            
            <div className="flex space-x-4 mb-6">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  aria-label={social.label}
                  className="p-2 bg-secondary/50 hover:bg-cyber-blue/20 border border-border/50 hover:border-cyber-blue/50 rounded-lg transition-all duration-300 group"
                >
                  <social.icon className="h-5 w-5 text-muted-foreground group-hover:text-cyber-blue transition-colors duration-300" />
                </a>
              ))}
            </div>

            {/* Security Badges */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <Shield className="h-4 w-4 text-safe-green" />
                <span>SOC 2 Type II Compliant</span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <Shield className="h-4 w-4 text-cyber-blue" />
                <span>ISO 27001 Certified</span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <Shield className="h-4 w-4 text-cyber-cyan" />
                <span>GDPR Compliant</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-border/50 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-muted-foreground">
              © {currentYear} ThreatShield. All rights reserved. Built with cutting-edge security technology.
            </div>
            
            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <span className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-safe-green rounded-full animate-pulse" />
                <span>System Status: Operational</span>
              </span>
              <span className="hidden md:block">|</span>
              <span>99.9% Uptime</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
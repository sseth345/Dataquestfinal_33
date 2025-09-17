import { Download, Smartphone, Monitor, Shield, Apple } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import mobileAppScreenshot from '@/assets/mobile-app-screenshot.jpg';
import appphoto from '@/assets/appphoto.png';

const DownloadApp = () => {
  return (
    <section id="download" className="py-20 bg-secondary/20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="text-foreground">Download </span>
            <span className="bg-gradient-primary bg-clip-text text-transparent">ThreatShield</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Take cybersecurity with you wherever you go. Our mobile and desktop applications 
            provide the same enterprise-grade protection with an intuitive interface.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 max-w-6xl mx-auto items-center">
          {/* Mobile App Preview */}
          <div className="relative animate-slide-up">
            <div className="relative max-w-sm mx-auto">
              {/* Phone Frame */}
              <div className="relative bg-gradient-card rounded-[2.5rem] p-2 border-2 border-border/50 shadow-card-custom">
                <div className="bg-background rounded-[2rem] overflow-hidden">
                  <img 
                    src={appphoto} 
                    alt="ThreatShield Mobile App"
                    className="w-full h-auto"
                  />
                </div>
              </div>
              
              {/* Floating elements */}
              <div className="absolute -top-4 -right-4 bg-safe-green/20 backdrop-blur-md rounded-full p-3 border border-safe-green/50 animate-glow-pulse">
                <Shield className="h-6 w-6 text-safe-green" />
              </div>
              <div className="absolute -bottom-4 -left-4 bg-cyber-blue/20 backdrop-blur-md rounded-full p-3 border border-cyber-blue/50 animate-glow-pulse" style={{animationDelay: '1s'}}>
                <Smartphone className="h-6 w-6 text-cyber-blue" />
              </div>
            </div>
          </div>

          {/* Download Options */}
          <div className="space-y-8 animate-slide-up" style={{animationDelay: '0.2s'}}>
            <div>
              <h3 className="text-3xl font-bold text-foreground mb-4">
                Protection at Your Fingertips
              </h3>
              <p className="text-muted-foreground text-lg leading-relaxed">
                Monitor threats, receive instant alerts, and manage your security posture 
                from anywhere. Available on all major platforms with seamless synchronization.
              </p>
            </div>

            {/* Download Buttons */}
           <div className="space-y-4">
  <div className="flex justify-center">
    <Button 
      asChild
      size="lg" 
      className="bg-gradient-primary hover:shadow-glow transition-all duration-300 transform hover:scale-105 h-16 px-8"
    >
      <a 
        href="https://drive.google.com/drive/folders/1kZIkFRuqnvBK4ltcgzHuKlEgj3Q7sltL" 
        target="_blank" 
        rel="noopener noreferrer"
        className="flex items-center"
      >
        <div className="mr-3 text-2xl">📱</div>
        <div className="text-left">
          <div className="text-sm opacity-90">Get it on</div>
          <div className="text-lg font-semibold">Google Play</div>
        </div>
      </a>
    </Button>
  </div>
</div>


            {/* Features */}
            <Card className="bg-gradient-card border-border/50">
              <CardContent className="p-6">
                <h4 className="font-semibold text-foreground mb-4">What's Included</h4>
                <div className="grid md:grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-cyber-blue rounded-full" />
                    <span className="text-muted-foreground">Real-time threat alerts</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-cyber-cyan rounded-full" />
                    <span className="text-muted-foreground">Remote monitoring</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-cyber-blue rounded-full" />
                    <span className="text-muted-foreground">Security dashboard</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-cyber-cyan rounded-full" />
                    <span className="text-muted-foreground">Instant notifications</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security Note */}
            <div className="bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Shield className="h-5 w-5 text-cyber-blue mt-0.5" />
                <div>
                  <p className="text-sm text-foreground font-medium mb-1">Secure Download</p>
                  <p className="text-xs text-muted-foreground">
                    All downloads are digitally signed and verified. No personal information required for basic protection.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DownloadApp;
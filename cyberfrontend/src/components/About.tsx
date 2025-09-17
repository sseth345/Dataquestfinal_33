import { useState, useEffect } from 'react';
import { Shield, Zap, Brain, Globe, Lock, AlertTriangle, TrendingUp, Activity, Users, Clock } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const About = () => {
  const [stats, setStats] = useState({
    detectionRate: 99.8,
    responseTime: 1.2,
    protectedSystems: 489150,
    activeUsers: 12730
  });

  const [counters, setCounters] = useState({
    detectionRate: 0,
    responseTime: 0,
    protectedSystems: 0,
    activeUsers: 0
  });

  // Real-time stats simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        detectionRate: Math.min(99.9, prev.detectionRate + (Math.random() * 0.02)),
        responseTime: Math.max(0.3, prev.responseTime + (Math.random() - 0.5) * 0.1),
        protectedSystems: prev.protectedSystems + Math.floor(Math.random() * 5),
        activeUsers: Math.max(12500, prev.activeUsers + Math.floor(Math.random() * 20) - 10)
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Counter animation
  useEffect(() => {
    const duration = 2000; // 2 seconds
    const steps = 60;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);

      setCounters({
        detectionRate: stats.detectionRate * easeOutCubic,
        responseTime: stats.responseTime * easeOutCubic,
        protectedSystems: Math.floor(stats.protectedSystems * easeOutCubic),
        activeUsers: Math.floor(stats.activeUsers * easeOutCubic)
      });

      if (currentStep >= steps) {
        clearInterval(timer);
        setCounters(stats);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [stats]);

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Detection',
      description: 'Advanced machine learning algorithms continuously analyze patterns to identify emerging threats and zero-day attacks.'
    },
    {
      icon: Zap,
      title: 'Real-Time Response',
      description: 'Instant threat neutralization with automated response systems that act within milliseconds of detection.'
    },
    {
      icon: Globe,
      title: 'Global Threat Intelligence',
      description: 'Connected to worldwide security networks providing real-time threat intelligence from across the globe.'
    },
    {
      icon: Lock,
      title: 'End-to-End Protection',
      description: 'Comprehensive security covering all attack vectors from network intrusions to malware and social engineering.'
    },
    {
      icon: AlertTriangle,
      title: 'Proactive Monitoring',
      description: '24/7 continuous monitoring with predictive analytics to prevent attacks before they happen.'
    },
    {
      icon: Shield,
      title: 'Enterprise Grade',
      description: 'Military-grade security protocols designed for enterprises with the highest security requirements.'
    }
  ];

  const renderStatCard = (iconComponent, value, suffix, label, sublabel, colorClass, trend = false) => {
    const IconComponent = iconComponent;
    return (
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-2xl blur-xl group-hover:opacity-30 transition-opacity duration-300"></div>
        <Card className="relative bg-gradient-to-br from-slate-900/90 to-slate-800/90 border border-blue-500/30 hover:border-blue-400/50 transition-all duration-300 backdrop-blur-sm">
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <IconComponent className={`h-6 w-6 ${colorClass} animate-pulse`} />
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-center space-x-1">
                <span className={`text-3xl md:text-4xl font-bold ${colorClass} tabular-nums`}>
                  {typeof value === 'number' ? value.toLocaleString() : value}
                </span>
                {suffix && <span className={`text-2xl ${colorClass}`}>{suffix}</span>}
                {trend && <TrendingUp className="h-4 w-4 text-green-400 animate-bounce" />}
              </div>
              <div className="text-sm text-gray-300 font-medium">{label}</div>
              {sublabel && (
                <div className="text-xs text-blue-400 animate-pulse flex items-center justify-center space-x-1">
                  <Activity className="h-3 w-3" />
                  <span>{sublabel}</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div>
      {/* Custom Styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          
          @keyframes slideUp {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          
          @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
            50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.5); }
          }
          
          @keyframes number-roll {
            0% { transform: translateY(20px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
          }

          .animate-fade-in {
            animation: fadeIn 1s ease-out;
          }
          
          .animate-slide-up {
            animation: slideUp 0.8s ease-out forwards;
            opacity: 0;
          }
          
          .animate-pulse-glow {
            animation: pulse-glow 3s ease-in-out infinite;
          }
          
          .animate-number-roll {
            animation: number-roll 0.5s ease-out;
          }
          
          .tabular-nums {
            font-variant-numeric: tabular-nums;
          }
        `
      }} />

      <section id="about" className="py-20 bg-secondary/20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="text-foreground">Next-Generation </span>
              <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-600 bg-clip-text text-transparent">Cybersecurity</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              ThreatShield represents the evolution of cybersecurity, leveraging artificial intelligence 
              and advanced analytics to provide unprecedented protection against modern cyber threats. 
              Our platform combines cutting-edge technology with intuitive design to deliver enterprise-grade 
              security that's accessible to organizations of all sizes.
            </p>
          </div>

          {/* Real-time Key Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            {renderStatCard(
              Shield,
              `${counters.detectionRate.toFixed(1)}%`,
              null,
              "Threat Detection Rate",
              "Real-time analysis",
              "text-blue-400",
              true
            )}
            
            {renderStatCard(
              Clock,
              counters.responseTime.toFixed(1),
              "ms",
              "Avg Response Time",
              "Real-time processing",
              "text-cyan-400",
              false
            )}
            
            {renderStatCard(
              Globe,
              Math.floor(counters.protectedSystems),
              null,
              "Protected Systems",
              `+${Math.floor(Math.random() * 50) + 10} today`,
              "text-green-400",
              true
            )}
            
            {renderStatCard(
              Users,
              Math.floor(counters.activeUsers),
              null,
              "Active Users Now",
              "Online",
              "text-purple-400",
              false
            )}
          </div>

          {/* Live Activity Indicator */}
          <div className="flex justify-center mb-16">
            <div className="flex items-center space-x-2 bg-gradient-to-r from-green-500/20 to-blue-500/20 px-4 py-2 rounded-full border border-green-400/30">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-400 font-medium">Live System Status: All Systems Operational</span>
              <Activity className="h-4 w-4 text-green-400 animate-pulse" />
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card 
                key={index} 
                className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border-slate-700/50 hover:border-blue-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/20 animate-slide-up group backdrop-blur-sm"
                style={{animationDelay: `${index * 0.1}s`}}
              >
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-colors duration-300 group-hover:scale-110 transform">
                      <feature.icon className="h-6 w-6 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground">{feature.title}</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Additional Info */}
          <div className="mt-16 text-center">
            <div className="bg-gradient-to-br from-slate-900/70 to-slate-800/70 border border-blue-500/30 rounded-2xl p-8 max-w-4xl mx-auto backdrop-blur-sm">
              <h3 className="text-2xl font-bold text-foreground mb-4">
                Trusted by Industry Leaders
              </h3>
              <p className="text-muted-foreground mb-6">
                From Fortune 500 companies to government agencies, ThreatGuard protects critical 
                infrastructure and sensitive data across industries worldwide.
              </p>
              <div className="flex justify-center items-center flex-wrap gap-4 opacity-70">
                {['Banking', 'Healthcare', 'Government', 'Technology', 'Manufacturing', 'Energy'].map((industry, index) => (
                  <div key={index} className="flex items-center">
                    <div className="text-sm font-medium px-3 py-1 bg-blue-500/10 rounded-full border border-blue-500/20 hover:border-blue-400/40 transition-colors duration-300">
                      {industry}
                    </div>
                    {index < 5 && <div className="w-1 h-1 bg-blue-400/50 rounded-full mx-2 hidden sm:block" />}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
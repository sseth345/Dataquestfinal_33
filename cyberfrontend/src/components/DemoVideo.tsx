import { useState, useEffect } from 'react';
import { Play, Monitor, Smartphone, Globe, Shield, AlertTriangle, Activity, Wifi, TrendingUp, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const DemoVideo = () => {
  const [threats, setThreats] = useState([
    { id: 1, type: 'Botnet', status: 'CRITICAL', time: 'Just Now', color: 'red' },
    { id: 2, type: 'Ransomware', status: 'BLOCKED', time: 'Just Now', color: 'green' },
    { id: 3, type: 'Phishing', status: 'MEDIUM', time: '2m ago', color: 'yellow' }
  ]);

  const [networkStats, setNetworkStats] = useState({
    inbound: 5156,
    outbound: 3925,
    threatsDetected: 658,
    cleanTraffic: 9590
  });

  const [nodes, setNodes] = useState([
    { id: 1, x: 50, y: 40, status: 'safe', size: 8 },
    { id: 2, x: 30, y: 60, status: 'warning', size: 6 },
    { id: 3, x: 70, y: 60, status: 'safe', size: 6 },
    { id: 4, x: 20, y: 80, status: 'safe', size: 4 },
    { id: 5, x: 80, y: 80, status: 'threat', size: 5 },
    { id: 6, x: 50, y: 75, status: 'safe', size: 4 }
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Update network stats
      setNetworkStats(prev => ({
        inbound: prev.inbound + Math.floor(Math.random() * 20) - 10,
        outbound: prev.outbound + Math.floor(Math.random() * 15) - 7,
        threatsDetected: prev.threatsDetected + Math.floor(Math.random() * 3),
        cleanTraffic: prev.cleanTraffic + Math.floor(Math.random() * 25) - 12
      }));

      // Animate nodes
      setNodes(prev => prev.map(node => ({
        ...node,
        x: node.x + (Math.random() - 0.5) * 2,
        y: node.y + (Math.random() - 0.5) * 2
      })));

      // Add new threats occasionally
      if (Math.random() < 0.3) {
        const threatTypes = ['DDoS', 'Malware', 'SQL Injection', 'XSS', 'Brute Force'];
        const statuses = ['BLOCKED', 'CRITICAL', 'MEDIUM'];
        const colors = ['green', 'red', 'yellow'];
        
        const newThreat = {
          id: Date.now(),
          type: threatTypes[Math.floor(Math.random() * threatTypes.length)],
          status: statuses[Math.floor(Math.random() * statuses.length)],
          time: 'Just Now',
          color: colors[Math.floor(Math.random() * colors.length)]
        };

        setThreats(prev => [newThreat, ...prev.slice(0, 2)]);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'safe': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'threat': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div>
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          
          @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
            50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.6); }
          }
          
          @keyframes scan-line {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(500%); }
          }

          @keyframes data-flow {
            0% { transform: translateX(-100%); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translateX(100%); opacity: 0; }
          }

          .animate-fade-in {
            animation: fadeIn 1s ease-out;
          }
          
          .animate-pulse-glow {
            animation: pulse-glow 2s ease-in-out infinite;
          }
          
          .scan-line {
            animation: scan-line 3s linear infinite;
          }
          
          .data-flow {
            animation: data-flow 2s ease-in-out infinite;
          }

          .threat-critical { color: #ef4444; background-color: rgba(239, 68, 68, 0.1); }
          .threat-blocked { color: #10b981; background-color: rgba(16, 185, 129, 0.1); }
          .threat-medium { color: #f59e0b; background-color: rgba(245, 158, 11, 0.1); }
        `
      }} />

      <section id="demo" className="py-20 bg-gradient-to-b from-slate-900 to-slate-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="text-foreground">See </span>
              <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-600 bg-clip-text text-transparent">ThreatShield</span>
              <span className="text-foreground"> in Action</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Watch how our advanced threat detection system identifies and neutralizes cyber attacks 
              in real-time, protecting your digital infrastructure 24/7.
            </p>
          </div>

          {/* Interactive Demo Dashboard */}
          <div className="max-w-7xl mx-auto mb-16">
            <div className="bg-gradient-to-br from-slate-900/95 to-slate-800/95 rounded-2xl border border-blue-500/30 overflow-hidden backdrop-blur-sm animate-pulse-glow">
              <div className="p-6">
                <div className="grid lg:grid-cols-3 gap-6 h-[500px]">
                  
                  {/* Live Threat Feed */}
                  <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white flex items-center">
                        <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
                        Live Threat Feed
                      </h3>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="text-xs text-green-400">Active</span>
                      </div>
                    </div>
                    
                    <div className="space-y-3 max-h-[400px] overflow-hidden">
                      {threats.map((threat, index) => (
                        <div 
                          key={threat.id} 
                          className={`p-3 rounded-lg border transition-all duration-300 ${
                            threat.status === 'CRITICAL' ? 'threat-critical border-red-500/50' :
                            threat.status === 'BLOCKED' ? 'threat-blocked border-green-500/50' :
                            'threat-medium border-yellow-500/50'
                          }`}
                          style={{ 
                            animation: `fadeIn 0.5s ease-out ${index * 0.1}s both`,
                            opacity: 1 - (index * 0.3)
                          }}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium text-sm">{threat.type}</div>
                              <div className="text-xs opacity-70">{threat.time}</div>
                            </div>
                            <div className={`text-xs px-2 py-1 rounded ${
                              threat.status === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                              threat.status === 'BLOCKED' ? 'bg-green-500/20 text-green-400' :
                              'bg-yellow-500/20 text-yellow-400'
                            }`}>
                              {threat.status}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Network Visualization */}
                  <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-4 relative overflow-hidden">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                      <Activity className="h-5 w-5 text-blue-400 mr-2" />
                      Network Monitor
                    </h3>
                    
                    {/* Central Node */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="relative">
                        <div className="w-16 h-16 bg-blue-500/20 rounded-full border-2 border-blue-400 flex items-center justify-center animate-pulse">
                          <Shield className="h-8 w-8 text-blue-400" />
                        </div>
                        
                        {/* Scanning Effect */}
                        <div className="absolute inset-0 rounded-full overflow-hidden">
                          <div className="w-full h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent scan-line"></div>
                        </div>
                      </div>
                    </div>

                    {/* Network Nodes */}
                    {nodes.map(node => (
                      <div
                        key={node.id}
                        className="absolute w-3 h-3 rounded-full transition-all duration-1000 animate-pulse"
                        style={{
                          left: `${Math.max(10, Math.min(90, node.x))}%`,
                          top: `${Math.max(10, Math.min(90, node.y))}%`,
                          backgroundColor: getStatusColor(node.status),
                          boxShadow: `0 0 ${node.size}px ${getStatusColor(node.status)}`,
                        }}
                      />
                    ))}

                    {/* Data Flow Lines */}
                    <div className="absolute inset-0 pointer-events-none">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className="absolute h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent data-flow"
                          style={{
                            top: `${30 + i * 20}%`,
                            animationDelay: `${i * 0.7}s`
                          }}
                        />
                      ))}
                    </div>

                    {/* Play Demo Button Overlay */}
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                      <Button className="bg-blue-500/20 backdrop-blur-md border border-blue-400/50 text-blue-400 hover:bg-blue-500 hover:text-white transition-all duration-300 text-xs px-3 py-1">
                        <Play className="mr-1 h-3 w-3 fill-current" />
                        Watch Live Demo
                      </Button>
                    </div>
                  </div>

                  {/* Network Statistics */}
                  <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-4">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                      <TrendingUp className="h-5 w-5 text-green-400 mr-2" />
                      Network Statistics
                    </h3>
                    
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-300">Inbound Traffic</span>
                          <TrendingUp className="h-4 w-4 text-blue-400" />
                        </div>
                        <div className="text-2xl font-bold text-blue-400 mb-1">
                          {networkStats.inbound.toLocaleString()}
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div className="bg-gradient-to-r from-blue-500 to-cyan-400 h-2 rounded-full transition-all duration-1000" style={{width: '75%'}}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-300">Outbound Traffic</span>
                          <TrendingUp className="h-4 w-4 text-cyan-400" />
                        </div>
                        <div className="text-2xl font-bold text-cyan-400 mb-1">
                          {networkStats.outbound.toLocaleString()}
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div className="bg-gradient-to-r from-cyan-500 to-blue-400 h-2 rounded-full transition-all duration-1000" style={{width: '60%'}}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-300">Threats Detected</span>
                          <AlertTriangle className="h-4 w-4 text-red-400" />
                        </div>
                        <div className="text-2xl font-bold text-red-400 mb-1">
                          {networkStats.threatsDetected}
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div className="bg-gradient-to-r from-red-500 to-orange-400 h-2 rounded-full transition-all duration-1000" style={{width: '15%'}}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-300">Clean Traffic</span>
                          <Shield className="h-4 w-4 text-green-400" />
                        </div>
                        <div className="text-2xl font-bold text-green-400 mb-1">
                          {networkStats.cleanTraffic.toLocaleString()}
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div className="bg-gradient-to-r from-green-500 to-emerald-400 h-2 rounded-full transition-all duration-1000" style={{width: '85%'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Platform Showcase */}
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="bg-gradient-to-br from-slate-900/70 to-slate-800/70 border-slate-700/50 hover:border-blue-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/20 backdrop-blur-sm">
              <CardContent className="p-6 text-center">
                <div className="flex justify-center mb-4">
                  <div className="p-4 bg-blue-500/10 rounded-full hover:bg-blue-500/20 transition-colors duration-300">
                    <Monitor className="h-8 w-8 text-blue-400" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Desktop Dashboard</h3>
                <p className="text-muted-foreground text-sm">
                  Comprehensive threat monitoring and management from your desktop with real-time analytics and reporting.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/70 to-slate-800/70 border-slate-700/50 hover:border-cyan-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/20 backdrop-blur-sm">
              <CardContent className="p-6 text-center">
                <div className="flex justify-center mb-4">
                  <div className="p-4 bg-cyan-500/10 rounded-full hover:bg-cyan-500/20 transition-colors duration-300">
                    <Smartphone className="h-8 w-8 text-cyan-400" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Mobile App</h3>
                <p className="text-muted-foreground text-sm">
                  Stay protected on-the-go with our mobile app featuring instant alerts and remote monitoring capabilities.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/70 to-slate-800/70 border-slate-700/50 hover:border-blue-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/20 backdrop-blur-sm">
              <CardContent className="p-6 text-center">
                <div className="flex justify-center mb-4">
                  <div className="p-4 bg-blue-500/10 rounded-full hover:bg-blue-500/20 transition-colors duration-300">
                    <Globe className="h-8 w-8 text-blue-400" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Web Portal</h3>
                <p className="text-muted-foreground text-sm">
                  Access your security dashboard from anywhere with our cloud-based web portal and advanced analytics.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DemoVideo;
"""
Application usage collector for monitoring application launches and usage patterns.
"""

import psutil
import platform
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
import os
import json

if platform.system() == "Windows":
    try:
        import wmi
        import win32gui
        import win32process
        WMI_AVAILABLE = True
    except ImportError:
        WMI_AVAILABLE = False
else:
    WMI_AVAILABLE = False

from .base_collector import BaseCollector


class ApplicationUsageCollector(BaseCollector):
    """
    Collects application usage and launch events.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.last_check_time = datetime.now() - timedelta(hours=1)
        self.tracked_processes = {}  # pid -> process_info
        self.application_sessions = {}  # app_name -> session_info
        self.current_user = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        self.hostname = os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'unknown'))
        
        # Initialize WMI connection if available
        if WMI_AVAILABLE:
            try:
                self.wmi_conn = wmi.WMI()
            except:
                self.wmi_conn = None
                WMI_AVAILABLE = False
    
    def get_collector_name(self) -> str:
        return "ApplicationUsageCollector"
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect application usage data.
        
        Returns:
            List of application usage event dictionaries
        """
        events = []
        
        # Collect current running applications
        events.extend(self._collect_running_applications())
        
        # Collect application launch events
        events.extend(self._collect_application_launches())
        
        # Analyze application usage patterns
        events.extend(self._analyze_usage_patterns())
        
        # Update tracking data
        self._update_tracking_data()
        
        self.last_check_time = datetime.now()
        
        return events
    
    def _collect_running_applications(self) -> List[Dict[str, Any]]:
        """Collect information about currently running applications."""
        events = []
        current_processes = {}
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'exe', 'create_time', 'cpu_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    
                    # Filter for current user processes
                    if proc_info['username'] != self.current_user:
                        continue
                    
                    pid = proc_info['pid']
                    proc_name = proc_info['name']
                    exe_path = proc_info.get('exe', '')
                    
                    # Skip system processes
                    if self._is_system_process(proc_name, exe_path):
                        continue
                    
                    current_processes[pid] = {
                        'pid': pid,
                        'name': proc_name,
                        'exe_path': exe_path,
                        'create_time': proc_info['create_time'],
                        'cpu_percent': proc_info.get('cpu_percent', 0),
                        'memory_mb': proc_info.get('memory_info', {}).get('rss', 0) / (1024 * 1024),
                        'last_seen': time.time()
                    }
                    
                    # Check if this is a new process
                    if pid not in self.tracked_processes:
                        start_time = datetime.fromtimestamp(proc_info['create_time'])
                        
                        # Only include processes started since last check
                        if start_time > self.last_check_time:
                            event_data = {
                                'pid': pid,
                                'application_name': proc_name,
                                'executable_path': exe_path,
                                'start_time': start_time.isoformat(),
                                'user_id': self.current_user,
                                'machine_name': self.hostname,
                                'memory_usage_mb': current_processes[pid]['memory_mb'],
                                'risk_score': self._assess_application_risk(proc_name, exe_path)
                            }
                            
                            formatted_event = self.format_event(
                                event_data,
                                'application_launch',
                                self.current_user
                            )
                            events.append(formatted_event)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error collecting running applications: {str(e)}")
        
        # Update tracked processes
        self.tracked_processes = current_processes
        
        return events
    
    def _collect_application_launches(self) -> List[Dict[str, Any]]:
        """Collect application launch events using system-specific methods."""
        events = []
        
        if platform.system() == "Windows" and WMI_AVAILABLE:
            events.extend(self._collect_windows_app_launches())
        
        return events
    
    def _collect_windows_app_launches(self) -> List[Dict[str, Any]]:
        """Collect Windows application launches using WMI."""
        events = []
        
        if not self.wmi_conn:
            return events
        
        try:
            # Query for process creation events
            # Note: This requires elevated privileges or specific WMI settings
            processes = self.wmi_conn.Win32_Process()
            
            for process in processes:
                if process.GetOwner()[2] == self.current_user:
                    creation_date = process.CreationDate
                    
                    if creation_date:
                        # Convert WMI datetime to Python datetime
                        # This is a simplified conversion
                        try:
                            timestamp = datetime.strptime(creation_date.split('.')[0], '%Y%m%d%H%M%S')
                            
                            if timestamp > self.last_check_time:
                                event_data = {
                                    'pid': process.ProcessId,
                                    'application_name': process.Name,
                                    'executable_path': process.ExecutablePath or '',
                                    'command_line': process.CommandLine or '',
                                    'parent_pid': process.ParentProcessId,
                                    'start_time': timestamp.isoformat(),
                                    'user_id': self.current_user,
                                    'machine_name': self.hostname,
                                    'risk_score': self._assess_application_risk(process.Name, process.ExecutablePath or '')
                                }
                                
                                formatted_event = self.format_event(
                                    event_data,
                                    'windows_process_creation',
                                    self.current_user
                                )
                                events.append(formatted_event)
                        
                        except ValueError:
                            continue
        
        except Exception as e:
            self.logger.error(f"Error collecting Windows app launches: {str(e)}")
        
        return events
    
    def _analyze_usage_patterns(self) -> List[Dict[str, Any]]:
        """Analyze application usage patterns for anomalies."""
        events = []
        
        # Count applications by type
        app_categories = self._categorize_applications()
        
        # Check for unusual application usage
        events.extend(self._detect_unusual_applications(app_categories))
        
        # Check for excessive application launches
        events.extend(self._detect_excessive_launches())
        
        # Check for off-hours usage
        events.extend(self._detect_off_hours_usage())
        
        return events
    
    def _categorize_applications(self) -> Dict[str, List[str]]:
        """Categorize applications by type."""
        categories = {
            'browsers': [],
            'development_tools': [],
            'office_apps': [],
            'system_tools': [],
            'media_apps': [],
            'security_tools': [],
            'remote_access': [],
            'unknown': []
        }
        
        # Define application patterns
        patterns = {
            'browsers': ['chrome', 'firefox', 'edge', 'safari', 'opera', 'browser'],
            'development_tools': ['python', 'java', 'code', 'studio', 'git', 'npm', 'node'],
            'office_apps': ['word', 'excel', 'powerpoint', 'outlook', 'office', 'libreoffice'],
            'system_tools': ['cmd', 'powershell', 'terminal', 'taskmgr', 'regedit'],
            'media_apps': ['vlc', 'media', 'player', 'spotify', 'music'],
            'security_tools': ['antivirus', 'defender', 'firewall', 'wireshark'],
            'remote_access': ['teamviewer', 'vnc', 'rdp', 'ssh', 'putty', 'remote']
        }
        
        for pid, proc_info in self.tracked_processes.items():
            app_name = proc_info['name'].lower()
            exe_path = proc_info['exe_path'].lower()
            
            categorized = False
            for category, keywords in patterns.items():
                if any(keyword in app_name or keyword in exe_path for keyword in keywords):
                    categories[category].append(app_name)
                    categorized = True
                    break
            
            if not categorized:
                categories['unknown'].append(app_name)
        
        return categories
    
    def _detect_unusual_applications(self, app_categories: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Detect unusual application usage patterns."""
        events = []
        
        # Check for unusual security tools
        if len(app_categories['security_tools']) > 0:
            event_data = {
                'anomaly_type': 'security_tools_usage',
                'applications': app_categories['security_tools'],
                'count': len(app_categories['security_tools']),
                'user_id': self.current_user,
                'machine_name': self.hostname,
                'risk_score': 0.6
            }
            
            formatted_event = self.format_event(
                event_data,
                'unusual_application_usage',
                self.current_user
            )
            events.append(formatted_event)
        
        # Check for remote access tools
        if len(app_categories['remote_access']) > 0:
            event_data = {
                'anomaly_type': 'remote_access_tools',
                'applications': app_categories['remote_access'],
                'count': len(app_categories['remote_access']),
                'user_id': self.current_user,
                'machine_name': self.hostname,
                'risk_score': 0.7
            }
            
            formatted_event = self.format_event(
                event_data,
                'remote_access_usage',
                self.current_user
            )
            events.append(formatted_event)
        
        return events
    
    def _detect_excessive_launches(self) -> List[Dict[str, Any]]:
        """Detect excessive application launches."""
        events = []
        
        current_time = time.time()
        recent_launches = len([p for p in self.tracked_processes.values() 
                             if current_time - p['create_time'] < 3600])  # Last hour
        
        if recent_launches > 20:  # More than 20 app launches in an hour
            event_data = {
                'anomaly_type': 'excessive_application_launches',
                'launch_count': recent_launches,
                'time_window': '1_hour',
                'user_id': self.current_user,
                'machine_name': self.hostname,
                'risk_score': min(0.8, recent_launches / 50.0)
            }
            
            formatted_event = self.format_event(
                event_data,
                'excessive_app_launches',
                self.current_user
            )
            events.append(formatted_event)
        
        return events
    
    def _detect_off_hours_usage(self) -> List[Dict[str, Any]]:
        """Detect application usage outside normal business hours."""
        events = []
        
        current_hour = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        is_off_hours = current_hour < 7 or current_hour > 19 or is_weekend
        
        if is_off_hours and len(self.tracked_processes) > 5:
            event_data = {
                'anomaly_type': 'off_hours_usage',
                'hour': current_hour,
                'is_weekend': is_weekend,
                'active_applications': len(self.tracked_processes),
                'user_id': self.current_user,
                'machine_name': self.hostname,
                'risk_score': 0.4 if is_weekend else 0.3
            }
            
            formatted_event = self.format_event(
                event_data,
                'off_hours_activity',
                self.current_user
            )
            events.append(formatted_event)
        
        return events
    
    def _update_tracking_data(self):
        """Update application session tracking data."""
        current_time = time.time()
        
        # Clean up old process data
        old_pids = [pid for pid, info in self.tracked_processes.items() 
                   if current_time - info.get('last_seen', 0) > 300]  # 5 minutes
        
        for pid in old_pids:
            del self.tracked_processes[pid]
        
        # Update application session data
        for pid, proc_info in self.tracked_processes.items():
            app_name = proc_info['name']
            
            if app_name not in self.application_sessions:
                self.application_sessions[app_name] = {
                    'first_seen': proc_info['create_time'],
                    'last_seen': current_time,
                    'total_launches': 1,
                    'active_time': 0
                }
            else:
                self.application_sessions[app_name]['last_seen'] = current_time
                self.application_sessions[app_name]['active_time'] = (
                    current_time - self.application_sessions[app_name]['first_seen']
                )
    
    def _is_system_process(self, proc_name: str, exe_path: str) -> bool:
        """Determine if a process is a system process that should be ignored."""
        system_processes = {
            'system', 'registry', 'smss.exe', 'csrss.exe', 'winlogon.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'spoolsv.exe',
            'explorer.exe', 'dwm.exe', 'taskhost.exe', 'conhost.exe',
            'wininit.exe', 'winlogon.exe', 'audiodg.exe', 'dllhost.exe'
        }
        
        system_paths = {
            'c:\\windows\\system32', 'c:\\windows\\syswow64',
            '/usr/bin', '/usr/sbin', '/bin', '/sbin'
        }
        
        proc_name_lower = proc_name.lower()
        exe_path_lower = exe_path.lower()
        
        # Check process name
        if proc_name_lower in system_processes:
            return True
        
        # Check executable path
        for sys_path in system_paths:
            if sys_path in exe_path_lower:
                return True
        
        return False
    
    def _assess_application_risk(self, app_name: str, exe_path: str) -> float:
        """Assess the risk level of an application."""
        risk_score = 0.1  # Base risk
        
        app_name_lower = app_name.lower()
        exe_path_lower = exe_path.lower()
        
        # High-risk applications
        high_risk_apps = {
            'cmd.exe', 'powershell.exe', 'regedit.exe', 'taskmgr.exe',
            'wireshark.exe', 'nmap.exe', 'netcat.exe', 'putty.exe',
            'teamviewer.exe', 'vnc', 'rdp', 'tor.exe'
        }
        
        # Medium-risk applications
        medium_risk_apps = {
            'python.exe', 'java.exe', 'node.exe', 'git.exe',
            'chrome.exe', 'firefox.exe', 'code.exe'
        }
        
        # Check application name
        if any(high_risk in app_name_lower for high_risk in high_risk_apps):
            risk_score += 0.6
        elif any(medium_risk in app_name_lower for medium_risk in medium_risk_apps):
            risk_score += 0.3
        
        # Check for portable/temp applications
        if 'temp' in exe_path_lower or 'tmp' in exe_path_lower:
            risk_score += 0.4
        
        # Check for unsigned or unusual locations
        suspicious_paths = ['downloads', 'desktop', 'documents', 'appdata\\roaming']
        if any(sus_path in exe_path_lower for sus_path in suspicious_paths):
            risk_score += 0.2
        
        return min(risk_score, 1.0)
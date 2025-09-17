"""
System events collector for monitoring login/logout events and system commands.
"""

import psutil
import platform
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import getpass
import socket

# Windows-specific imports
if platform.system() == "Windows":
    try:
        import wmi
        import win32evtlog
        import win32evtlogutil
        import win32security
    except ImportError:
        wmi = None
        win32evtlog = None

from .base_collector import BaseCollector


class SystemEventsCollector(BaseCollector):
    """
    Collects system events including login/logout times and system commands.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.last_check_time = datetime.now() - timedelta(hours=1)
        self.current_user = getpass.getuser()
        self.hostname = socket.gethostname()
        
    def get_collector_name(self) -> str:
        return "SystemEventsCollector"
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect system events data.
        
        Returns:
            List of system event dictionaries
        """
        events = []
        
        # Collect login/logout events
        login_events = self._collect_login_events()
        events.extend(login_events)
        
        # Collect system command events
        command_events = self._collect_command_events()
        events.extend(command_events)
        
        # Collect process events
        process_events = self._collect_process_events()
        events.extend(process_events)
        
        # Update last check time
        self.last_check_time = datetime.now()
        
        return events
    
    def _collect_login_events(self) -> List[Dict[str, Any]]:
        """
        Collect login/logout events based on the operating system.
        
        Returns:
            List of login event dictionaries
        """
        events = []
        
        if platform.system() == "Windows":
            events.extend(self._collect_windows_login_events())
        else:
            events.extend(self._collect_unix_login_events())
        
        return events
    
    def _collect_windows_login_events(self) -> List[Dict[str, Any]]:
        """
        Collect Windows login events from Event Log.
        
        Returns:
            List of Windows login event dictionaries
        """
        events = []
        
        if not win32evtlog:
            self.logger.warning("Windows event log libraries not available")
            return events
        
        try:
            # Open Security event log
            handle = win32evtlog.OpenEventLog(None, "Security")
            
            # Event IDs for login/logout events
            login_event_ids = [4624, 4625, 4634, 4647]  # Logon success, failure, logoff
            
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            while True:
                events_batch = win32evtlog.ReadEventLog(handle, flags, 0)
                if not events_batch:
                    break
                
                for event in events_batch:
                    if event.EventID in login_event_ids:
                        event_time = event.TimeGenerated
                        
                        # Only collect events since last check
                        if event_time > self.last_check_time:
                            event_data = {
                                'event_id': event.EventID,
                                'timestamp': event_time.isoformat(),
                                'source_ip': self._extract_source_ip(event),
                                'machine_name': self.hostname,
                                'user_id': self._extract_user_id(event),
                                'event_type': self._get_login_event_type(event.EventID),
                                'success': event.EventID in [4624, 4634, 4647]
                            }
                            
                            formatted_event = self.format_event(
                                event_data, 
                                event_data['event_type'], 
                                event_data['user_id']
                            )
                            events.append(formatted_event)
            
            win32evtlog.CloseEventLog(handle)
            
        except Exception as e:
            self.logger.error(f"Error collecting Windows login events: {str(e)}")
        
        return events
    
    def _collect_unix_login_events(self) -> List[Dict[str, Any]]:
        """
        Collect Unix/Linux login events from system logs.
        
        Returns:
            List of Unix login event dictionaries
        """
        events = []
        
        try:
            # Try to read from wtmp for login/logout events
            try:
                result = subprocess.run(['last', '-n', '100'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    events.extend(self._parse_last_output(result.stdout))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.warning("'last' command not available or timed out")
            
            # Try to read from auth logs
            auth_log_paths = ['/var/log/auth.log', '/var/log/secure']
            for log_path in auth_log_paths:
                try:
                    with open(log_path, 'r') as f:
                        lines = f.readlines()[-1000:]  # Read last 1000 lines
                        events.extend(self._parse_auth_log(lines))
                    break
                except (FileNotFoundError, PermissionError):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error collecting Unix login events: {str(e)}")
        
        return events
    
    def _collect_command_events(self) -> List[Dict[str, Any]]:
        """
        Collect system command execution events.
        
        Returns:
            List of command event dictionaries
        """
        events = []
        
        try:
            # Monitor bash/shell history for recent commands
            history_paths = [
                f"/home/{self.current_user}/.bash_history",
                f"/home/{self.current_user}/.zsh_history",
                f"C:\\Users\\{self.current_user}\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt"
            ]
            
            for history_path in history_paths:
                try:
                    with open(history_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[-100:]  # Get last 100 commands
                        
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                event_data = {
                                    'command': line,
                                    'timestamp': datetime.now().isoformat(),
                                    'user_id': self.current_user,
                                    'machine_name': self.hostname,
                                    'risk_level': self._assess_command_risk(line)
                                }
                                
                                formatted_event = self.format_event(
                                    event_data, 
                                    'command_execution', 
                                    self.current_user
                                )
                                events.append(formatted_event)
                    
                    break  # If we successfully read one history file, don't try others
                
                except (FileNotFoundError, PermissionError):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error collecting command events: {str(e)}")
        
        return events
    
    def _collect_process_events(self) -> List[Dict[str, Any]]:
        """
        Collect running process information.
        
        Returns:
            List of process event dictionaries
        """
        events = []
        
        try:
            current_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time', 'exe']):
                try:
                    proc_info = proc.info
                    if proc_info['username'] == self.current_user:
                        process_data = {
                            'pid': proc_info['pid'],
                            'process_name': proc_info['name'],
                            'executable_path': proc_info.get('exe', ''),
                            'start_time': datetime.fromtimestamp(proc_info['create_time']).isoformat(),
                            'user_id': self.current_user,
                            'machine_name': self.hostname
                        }
                        
                        # Only include processes started recently
                        start_time = datetime.fromtimestamp(proc_info['create_time'])
                        if start_time > self.last_check_time:
                            formatted_event = self.format_event(
                                process_data, 
                                'process_start', 
                                self.current_user
                            )
                            events.append(formatted_event)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error collecting process events: {str(e)}")
        
        return events
    
    def _extract_source_ip(self, event) -> str:
        """Extract source IP from Windows event log entry."""
        try:
            # This is a simplified extraction - in practice, you'd need to parse
            # the event data more thoroughly
            return "127.0.0.1"  # Placeholder
        except:
            return ""
    
    def _extract_user_id(self, event) -> str:
        """Extract user ID from Windows event log entry."""
        try:
            # Simplified extraction - would need proper parsing in practice
            return self.current_user
        except:
            return ""
    
    def _get_login_event_type(self, event_id: int) -> str:
        """Map Windows event ID to event type."""
        event_type_map = {
            4624: 'login_success',
            4625: 'login_failure',
            4634: 'logout',
            4647: 'logout_initiated'
        }
        return event_type_map.get(event_id, 'unknown_login_event')
    
    def _parse_last_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse output from 'last' command."""
        events = []
        lines = output.strip().split('\n')
        
        for line in lines[:-1]:  # Skip last line (wtmp begins...)
            parts = line.split()
            if len(parts) >= 7:
                user = parts[0]
                terminal = parts[1]
                host = parts[2] if parts[2] != 'console' else 'localhost'
                
                # Parse date/time - this is simplified
                date_str = ' '.join(parts[3:7])
                
                event_data = {
                    'user_id': user,
                    'terminal': terminal,
                    'source_ip': host,
                    'timestamp': datetime.now().isoformat(),  # Simplified
                    'machine_name': self.hostname
                }
                
                formatted_event = self.format_event(
                    event_data, 
                    'login_session', 
                    user
                )
                events.append(formatted_event)
        
        return events
    
    def _parse_auth_log(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse authentication log lines."""
        events = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['login', 'session', 'authentication']):
                # Simplified parsing - would need more robust parsing in practice
                parts = line.split()
                if len(parts) >= 5:
                    timestamp = ' '.join(parts[:3])
                    
                    event_data = {
                        'log_line': line.strip(),
                        'timestamp': datetime.now().isoformat(),  # Simplified
                        'machine_name': self.hostname
                    }
                    
                    formatted_event = self.format_event(
                        event_data, 
                        'auth_event', 
                        self.current_user
                    )
                    events.append(formatted_event)
        
        return events
    
    def _assess_command_risk(self, command: str) -> float:
        """
        Assess the risk level of a command.
        
        Args:
            command: Command string
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        high_risk_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk', 'dd if=', 'wget', 'curl',
            'ssh', 'scp', 'nc ', 'netcat', 'powershell', 'cmd.exe',
            'regedit', 'gpedit', 'net user', 'net localgroup'
        ]
        
        medium_risk_commands = [
            'chmod 777', 'chown', 'sudo', 'su ', 'mount', 'umount',
            'iptables', 'ufw', 'firewall', 'taskkill', 'wmic'
        ]
        
        command_lower = command.lower()
        
        for high_risk_cmd in high_risk_commands:
            if high_risk_cmd in command_lower:
                return 0.8
        
        for medium_risk_cmd in medium_risk_commands:
            if medium_risk_cmd in command_lower:
                return 0.5
        
        return 0.1  # Low risk for other commands
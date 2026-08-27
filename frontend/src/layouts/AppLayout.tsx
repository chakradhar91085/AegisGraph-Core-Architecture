import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { UserButton } from '@clerk/clerk-react';
import { MessageSquare, Activity, ScrollText, RefreshCw, ArrowLeft } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { messages, endActiveSession } = useChat();

  const handleEndSession = async () => {
    await endActiveSession();
    if (location.pathname !== '/app') {
      navigate('/app');
    }
  };

  const navItems = [
    { name: 'Query Playground', path: '/app', icon: MessageSquare, exact: true },
    { name: 'Security Dashboard', path: '/app/security', icon: Activity },
    { name: 'System Logs', path: '/app/logs', icon: ScrollText },
  ];

  return (
    <div className="flex h-screen w-screen bg-[#050505] text-[#f2ede6] font-sans overflow-hidden">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-[#1e1e1e] bg-[#080808] flex flex-col shrink-0">
        
        {/* Brand */}
        <div className="h-16 px-6 flex items-center gap-3 border-b border-[#1e1e1e] shrink-0">
          <div className="relative flex items-center justify-center w-5 h-5 text-[#2196f3]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full drop-shadow-[0_0_8px_rgba(33,150,243,0.2)]">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <circle cx="12" cy="9" r="1.5" fill="currentColor" />
              <circle cx="8.5" cy="14" r="1.5" fill="currentColor" />
              <circle cx="15.5" cy="14" r="1.5" fill="currentColor" />
              <path d="M12 9l-3.5 5M12 9l3.5 5M8.5 14h7" strokeWidth="1" strokeDasharray="1 2" opacity="0.8" />
            </svg>
          </div>
          <span className="font-display tracking-[0.1em] font-bold italic text-lg text-[#f2ede6]">AEGISGRAPH</span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 flex flex-col gap-6 overflow-y-auto">
          
          <div>
            <div className="text-[10px] uppercase tracking-[0.2em] font-mono text-[#5a5a5a] mb-3 px-3">Knowledge</div>
            <div className="flex flex-col gap-1">
              {[navItems[0]].map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.exact}
                  className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm font-medium ${
                      isActive 
                        ? 'bg-[#2196f3]/10 text-[#2196f3]' 
                        : 'text-[#8a8a8a] hover:bg-[#141414] hover:text-[#f2ede6]'
                    }`
                  }
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </NavLink>
              ))}
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-[0.2em] font-mono text-[#5a5a5a] mb-3 px-3">Security</div>
            <div className="flex flex-col gap-1">
              {[navItems[1], navItems[2]].map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.exact}
                  className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm font-medium ${
                      isActive 
                        ? 'bg-[#2196f3]/10 text-[#2196f3]' 
                        : 'text-[#8a8a8a] hover:bg-[#141414] hover:text-[#f2ede6]'
                    }`
                  }
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </NavLink>
              ))}
            </div>
          </div>
        </nav>

        {/* System Health Panel */}
        <div className="mx-4 mb-4 p-4 bg-[#0a0a0a] border border-[#1e1e1e] rounded-sm relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#2196f3]/50 to-transparent"></div>
          <div className="flex flex-col gap-2 relative z-10">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-[#8a8a8a] font-mono uppercase tracking-wider">Aegis Engine</span>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-[10px] text-green-500 font-mono uppercase tracking-wider">Online</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-[#8a8a8a] font-mono uppercase tracking-wider">Behavior Mon</span>
              <span className="text-[10px] text-[#2196f3] font-mono uppercase tracking-wider">Active</span>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-[#1e1e1e] flex flex-col gap-3 shrink-0">
          <button 
            onClick={handleEndSession}
            className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-[#8a8a8a] hover:text-[#f2ede6] hover:bg-[#141414] rounded-md transition-colors w-full"
          >
            <RefreshCw className="w-4 h-4" />
            {messages.length > 0 ? "End Session" : "New Session"}
          </button>
          
          <div className="flex items-center justify-between px-3 py-2 mt-2">
            <UserButton afterSignOutUrl="/" appearance={{ elements: { userButtonAvatarBox: "w-8 h-8" } }} />
            <button 
              onClick={() => navigate('/')}
              className="text-[#8a8a8a] hover:text-[#f2ede6] text-xs font-mono uppercase tracking-widest transition-colors flex items-center gap-1"
            >
              <ArrowLeft className="w-3 h-3" />
              Exit
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex min-w-0 overflow-hidden relative">
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
          <Outlet />
        </div>
      </main>

    </div>
  );
}

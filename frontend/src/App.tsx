import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';
import { LandingPage } from './pages/LandingPage';
import { AppLayout } from './layouts/AppLayout';
import { QueryPlayground } from './pages/QueryPlayground';
import { SecurityDashboard } from './pages/SecurityDashboard';
import { SystemLogs } from './pages/SystemLogs';
import { ChatProvider } from './contexts/ChatContext';

function App() {
  return (
    <ChatProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
        
        {/* Protected App Routes */}
        <Route path="/app" element={
          <>
            <SignedIn>
              <AppLayout />
            </SignedIn>
            <SignedOut>
              <RedirectToSignIn />
            </SignedOut>
          </>
        }>
          {/* Nested Routes within AppLayout */}
          <Route index element={<QueryPlayground />} />
          <Route path="security" element={<SecurityDashboard />} />
          <Route path="logs" element={<SystemLogs />} />
        </Route>

        {/* Fallback to landing page for unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
    </ChatProvider>
  );
}

export default App;

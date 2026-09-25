import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, RedirectToSignIn, useAuth } from '@clerk/clerk-react';
import { setTokenGetter } from './api';
import { LandingPage } from './pages/LandingPage';
import { AppLayout } from './layouts/AppLayout';
import { QueryPlayground } from './pages/QueryPlayground';
import { SecurityDashboard } from './pages/SecurityDashboard';
import { SystemLogs } from './pages/SystemLogs';
import { ChatProvider } from './contexts/ChatContext';

// Hands the Clerk session token to the API client. Rendered before the router so
// it is registered before any page makes its first request.
function AuthBridge() {
  const { getToken } = useAuth();
  useEffect(() => {
    setTokenGetter(() => getToken());
  }, [getToken]);
  return null;
}

function App() {
  return (
    <ChatProvider>
      <AuthBridge />
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

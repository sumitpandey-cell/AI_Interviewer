import { ReactNode, useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthAPI } from '@/lib/api';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const location = useLocation();

  useEffect(() => {
    // Check if user is authenticated
    setIsAuthenticated(AuthAPI.isAuthenticated());
  }, []);

  if (isAuthenticated === null) {
    // Loading state while checking authentication
    return (
      <div className="flex items-center justify-center h-screen bg-dark-bg">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-12 w-12 text-primary animate-spin" />
          <p className="text-white text-lg">Verifying your access...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to home page with return URL
    return <Navigate to="/" state={{ from: location.pathname }} replace />;
  }

  // User is authenticated, render children
  return <>{children}</>;
};

export default ProtectedRoute;

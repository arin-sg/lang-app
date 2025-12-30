import { Link, Outlet, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="bg-card border-b border-border sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              {/* Logo */}
              <div className="flex-shrink-0 flex items-center gap-2 cursor-pointer">
                <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-md shadow-primary/20">
                  <span className="text-primary-foreground font-extrabold text-xl">🍌</span>
                </div>
                <span className="font-extrabold text-2xl tracking-tight text-foreground">
                  LingoFlow
                </span>
              </div>

              {/* Nav Links */}
              <div className="hidden sm:flex sm:space-x-8 h-full">
                <Link
                  to="/ingest"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-semibold transition-colors ${
                    isActive('/ingest')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                  }`}
                >
                  Ingest
                </Link>
                <Link
                  to="/library"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-semibold transition-colors ${
                    isActive('/library')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                  }`}
                >
                  Library
                </Link>
                <Link
                  to="/review"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-semibold transition-colors ${
                    isActive('/review')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                  }`}
                >
                  Review
                </Link>
                <Link
                  to="/coach"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-semibold transition-colors ${
                    isActive('/coach')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                  }`}
                >
                  Coach
                </Link>
              </div>
            </div>

            {/* Language Selector (placeholder) */}
            <div className="flex items-center">
              <div className="bg-secondary/50 text-secondary-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:bg-secondary transition-colors cursor-pointer">
                Current: German 🇩🇪
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <Outlet />
      </main>
    </div>
  );
}
